with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

old_query = """        SELECT 
            t.id as tipologia_id, 
            t.codigo_tipologia,
            t.nombre as oficial, 
            t.formatos_permitidos,
            st.obligatoria,
            st.orden_sugerido,
            doc.id as documento_id,
            doc.file_name,
            doc.created_at as fecha_carga,
            doc.uploaded_by as autor_carga,
            (CASE WHEN doc.id IS NOT NULL THEN 'CARGADO' ELSE 'FALTANTE' END) as estado_carga
        FROM agn_subserie_tipologia st
        INNER JOIN agn_tipologias t ON st.tipologia_id = t.id
        LEFT JOIN documents doc ON st.tipologia_id = doc.tipologia_id AND doc.agn_expediente_id = :eid AND (doc.status = 'COMPLETED' OR doc.status = 'ARCHIVED')
        WHERE st.subserie_id = :sid
        ORDER BY st.obligatoria DESC, st.orden_sugerido ASC NULLS LAST, t.nombre ASC"""

new_query = """        SELECT 
            t.id as tipologia_id, 
            t.codigo_tipologia,
            t.nombre as oficial, 
            t.formatos_permitidos,
            st.obligatoria,
            st.orden_sugerido,
            doc.id as documento_id,
            doc.file_name,
            doc.created_at as fecha_carga,
            u.username as autor_carga,
            (CASE WHEN doc.id IS NOT NULL THEN 'CARGADO' ELSE 'FALTANTE' END) as estado_carga
        FROM agn_subserie_tipologia st
        INNER JOIN agn_tipologias t ON st.tipologia_id = t.id
        LEFT JOIN documents doc ON st.tipologia_id = doc.tipologia_id AND doc.agn_expediente_id = :eid AND (doc.status = 'COMPLETED' OR doc.status = 'ARCHIVED')
        LEFT JOIN users u ON doc.uploaded_by = u.id
        WHERE st.subserie_id = :sid
        ORDER BY st.obligatoria DESC, st.orden_sugerido ASC NULLS LAST, t.nombre ASC"""

content = content.replace(old_query, new_query)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
