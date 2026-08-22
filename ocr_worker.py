import asyncio
import time
import fitz  # PyMuPDF
from sqlalchemy import text
from app.database import get_global_db_session
from rapidocr_onnxruntime import RapidOCR

print("[Worker] Inicializando modelos de PaddleOCR (RapidOCR ONNX)...")
default_engine = RapidOCR()
print("[Worker] Modelos de PaddleOCR cargados correctamente.")

async def process_document(db, doc_id, file_path, tenant_id):
    query_settings = text("SELECT ocr_use_angle_cls, ocr_languages, ocr_confidence_threshold, ocr_pdf_resolution_dpi FROM tenant_ocr_settings WHERE tenant_id = :t")
    res = await db.execute(query_settings, {"t": tenant_id})
    settings = res.fetchone()
    
    use_angle = True
    conf_thresh = 0.85
    dpi = 150
    if settings:
        use_angle, langs, conf_thresh, dpi = settings
    
    # Normalizar ruta para Docker (Linux)
    import os
    file_path = file_path.replace('\\', '/')
    
    print(f"[OCR] Procesando documento: {file_path}")
    engine = default_engine
    
    extracted_text_blocks = []
    total_confidence = 0
    total_blocks = 0
    
    try:
        if file_path.lower().endswith('.pdf'):
            # Convert PDF pages to images using PyMuPDF (No podemos usar asyncio.to_thread para todo si queremos actualizar DB por cada pagina)
            # Asi que lo haremos asincrono interrumpiendo por pagina
            doc = fitz.open(file_path)
            total_pages = len(doc)
            zoom = dpi / 72.0
            mat = fitz.Matrix(zoom, zoom)
            
            for page_num in range(total_pages):
                def extract_single_page():
                    page = doc.load_page(page_num)
                    t_accum = []
                    c_accum = 0
                    b_accum = 0
                    
                    ext_text = page.get_text()
                    if ext_text.strip():
                        t_accum.append(ext_text.strip())
                        
                    pix = page.get_pixmap(matrix=mat)
                    img_bytes = pix.tobytes("png")
                    result, _ = engine(img_bytes, use_angle_cls=use_angle)
                    
                    if result:
                        for (bbox, text_res, prob) in result:
                            t_accum.append(text_res)
                            c_accum += prob
                            b_accum += 1
                    return t_accum, c_accum, b_accum
                
                # Ejecutar el OCR de esta pagina en un hilo
                p_blocks, p_conf, p_b_count = await asyncio.to_thread(extract_single_page)
                
                extracted_text_blocks.extend(p_blocks)
                total_confidence += p_conf
                total_blocks += p_b_count
                
                # Update progress in DB!
                progress = int(((page_num + 1) / total_pages) * 100)
                # Cap at 99 so 100 is only when completely done
                if progress >= 100: progress = 99 
                
                await db.execute(text("UPDATE documents SET ocr_progress_percent = :p WHERE id = :id"), {"p": progress, "id": doc_id})
                await db.commit()
                print(f"[OCR] Doc {doc_id} -> Progreso: {progress}%")
                
        else:
            # Es una imagen (1 sola pagina)
            await db.execute(text("UPDATE documents SET ocr_progress_percent = 50 WHERE id = :id"), {"id": doc_id})
            await db.commit()
            
            def extract_img_sync():
                t_accum = []
                c_accum = 0
                b_accum = 0
                result, _ = engine(file_path, use_angle_cls=use_angle)
                if result:
                    for (bbox, text_res, prob) in result:
                        t_accum.append(text_res)
                        c_accum += prob
                        b_accum += 1
                return t_accum, c_accum, b_accum
                
            p_blocks, p_conf, p_b_count = await asyncio.to_thread(extract_img_sync)
            extracted_text_blocks.extend(p_blocks)
            total_confidence += p_conf
            total_blocks += p_b_count

        extracted_text = "\\n".join(extracted_text_blocks).strip()
        avg_confidence = (total_confidence / total_blocks) if total_blocks > 0 else 1.0
        
        if avg_confidence < conf_thresh:
            extracted_text = "[REVISIÓN MANUAL REQUERIDA] \\n" + extracted_text
            
        query_update = text('''
            UPDATE documents
            SET status = 'COMPLETED', ocr_progress_percent = 100, extracted_text = :text, ocr_confidence_score = :score, updated_at = CURRENT_TIMESTAMP
            WHERE id = :id
        ''')
        await db.execute(query_update, {"text": extracted_text, "score": avg_confidence, "id": doc_id})
        await db.commit()
        print(f"[OCR] Fin exitoso para doc_id: {doc_id}")
        
    except Exception as e:
        print(f"[OCR] Error procesando archivo {file_path}: {e}")
        await db.execute(text("UPDATE documents SET status = 'FAILED', ocr_progress_percent = 0 WHERE id = :id"), {"id": doc_id})
        await db.commit()

async def run_worker():
    print("=========================================")
    print(" INICIANDO WORKER OCR (CON PROGRESO %)")
    print("=========================================")
    
    while True:
        try:
            async for db in get_global_db_session():
                query = text('''
                    UPDATE documents
                    SET status = 'EXTRACTING', ocr_progress_percent = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE id = (
                        SELECT id
                        FROM documents
                        WHERE status = 'PENDING'
                        ORDER BY created_at ASC
                        FOR UPDATE SKIP LOCKED
                        LIMIT 1
                    )
                    RETURNING id, tenant_id, file_path;
                ''')
                result = await db.execute(query)
                row = result.fetchone()
                
                if row:
                    doc_id, tenant_id, file_path = row
                    await db.commit()
                    try:
                        await process_document(db, doc_id, file_path, tenant_id)
                    except Exception as e:
                        print(f"Error procesando documento: {e}")
                        await db.execute(text("UPDATE documents SET status = 'FAILED' WHERE id = :id"), {"id": doc_id})
                        await db.commit()
                else:
                    await db.rollback()
                break
        except Exception as e:
            print(f"Error critico en Worker: {e}")
            
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(run_worker())
