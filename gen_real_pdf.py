with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re

# Add imports at the top
import_str = """
import os
from app.utils.pdf_generator import generar_pdf_fuid
from fastapi.responses import FileResponse
"""
content = content.replace("from fastapi.responses import PlainTextResponse", "from fastapi.responses import PlainTextResponse, FileResponse" + import_str)

# Modify firmar_fuid
old_firmar = """        # 3. Simulate PDF generation & Hash
        content_to_hash = f"{subserie_id}-{session_data['user_id']}-{datetime.now().isoformat()}".encode('utf-8')
        fuid_hash = hashlib.sha256(content_to_hash).hexdigest()
        
        # 4. Insert Transferencia
        transf_res = await db.execute(text('''
            INSERT INTO fuid_transferencias (subserie_id, consecutivo_oficial, usuario_firmante, hash_sha256, ruta_almacenamiento_pdf, tenant_id)
            VALUES (:sid, :consecutivo, :user_id, :hash, :ruta, :t)
            RETURNING id
        '''), {
            "sid": subserie_id, 
            "consecutivo": f"FUID-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "user_id": session_data["user_id"],
            "hash": fuid_hash,
            "ruta": f"/fuid_archives/{fuid_hash}.pdf",
            "t": session_data["tenant_id"]
        })
        fuid_id = transf_res.scalar()
        
        # 5. Insert Vinculos and Update expedientes"""

new_firmar = """        # 3. REAL PDF Generation & Hash
        sub_res = await db.execute(text("SELECT nombre FROM agn_subseries WHERE id = :sid"), {"sid": subserie_id})
        sub_nombre = sub_res.scalar()
        
        # Convert filas into simple dicts for the PDF generator
        registros_pdf = []
        for r in exp_validos:
            d = dict(r._mapping)
            d["no_orden"] = len(registros_pdf) + 1
            d["nombre_unidad_conservacion"] = d.get("nombre_expediente", "Expediente")
            d["fecha_inicial_str"] = "N/A"
            d["fecha_final_str"] = "N/A"
            d["caja_carpeta"] = "N/A"
            d["soporte"] = "ELECTRÓNICO"
            registros_pdf.append(d)
            
        pdf_bytes = generar_pdf_fuid(sub_nombre, registros_pdf)
        fuid_hash = hashlib.sha256(pdf_bytes).hexdigest()
        
        # Save to disk
        os.makedirs("fuid_archives", exist_ok=True)
        pdf_path = os.path.join("fuid_archives", f"{fuid_hash}.pdf")
        with open(pdf_path, "wb") as pdf_file:
            pdf_file.write(pdf_bytes)
        
        # 4. Insert Transferencia
        transf_res = await db.execute(text('''
            INSERT INTO fuid_transferencias (subserie_id, consecutivo_oficial, usuario_firmante, hash_sha256, ruta_almacenamiento_pdf, tenant_id)
            VALUES (:sid, :consecutivo, :user_id, :hash, :ruta, :t)
            RETURNING id
        '''), {
            "sid": subserie_id, 
            "consecutivo": f"FUID-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "user_id": session_data["user_id"],
            "hash": fuid_hash,
            "ruta": pdf_path,
            "t": session_data["tenant_id"]
        })
        fuid_id = transf_res.scalar()
        
        # 5. Insert Vinculos and Update expedientes"""
        
content = content.replace(old_firmar, new_firmar)

# Add PDF download endpoint
new_endpoint = """
@router.get("/fuid/descargar_pdf/{hash}")
async def descargar_pdf_fuid(
    hash: str,
    session_data: dict = Depends(require_permission("documentos:leer")),
    db: AsyncSession = Depends(get_db_session)
):
    pdf_path = os.path.join("fuid_archives", f"{hash}.pdf")
    if not os.path.exists(pdf_path):
        return JSONResponse({"status": "error", "detail": "PDF no encontrado"}, status_code=404)
        
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"FUID_{hash[:8]}.pdf")
"""
content += new_endpoint

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
