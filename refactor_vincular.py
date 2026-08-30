import re
with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace the foliation logic in vincular
old_vincular_start = """        # Calcular folios
        max_res = await db.execute(text("SELECT COALESCE(MAX(folio_fin), 0) FROM documents WHERE agn_expediente_id = :eid"), {"eid": expediente_id})
        max_folio = max_res.scalar()
        nuevo_folio_inicio = max_folio + 1
        nuevo_folio_fin = max_folio + pages
        
        # Vincular
        await db.execute(text('''
            UPDATE documents 
            SET agn_expediente_id = :eid, tipologia_id = :tid, folio = :f_ini, folio_fin = :f_fin
            WHERE id = :did
        '''), {
            "eid": expediente_id,
            "tid": req.tipologia_id,
            "f_ini": nuevo_folio_inicio,
            "f_fin": nuevo_folio_fin,
            "did": documento_id
        })"""

new_vincular_start = """        # El trigger TRG_DOCUMENTS_FOLIACION de Postgres hará el cálculo matemático de folio_inicio y folio_fin.
        # Solo le pasamos el paginas_cantidad.
        await db.execute(text('''
            UPDATE documents 
            SET agn_expediente_id = :eid, tipologia_id = :tid, paginas_cantidad = :pgs
            WHERE id = :did
        '''), {
            "eid": expediente_id,
            "tid": req.tipologia_id,
            "pgs": pages,
            "did": documento_id
        })
        
        # Recuperar los folios generados por el trigger para mostrarlos y enviarlos a la cadena de hash
        folios_res = await db.execute(text("SELECT folio, folio_fin FROM documents WHERE id = :did"), {"did": documento_id})
        folios_row = folios_res.fetchone()
        nuevo_folio_inicio = folios_row[0] if folios_row else 1
        nuevo_folio_fin = folios_row[1] if folios_row else pages"""

content = content.replace(old_vincular_start, new_vincular_start)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
