import re

with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    agn = f.read()

pattern = r"(# Obtener ultimo XML\n\s+idx_res = await db\.execute\(text\(\"SELECT \* FROM agn_indice_electronico WHERE expediente_id = :eid ORDER BY fecha_accion DESC LIMIT 1\"\), \{\"eid\": expediente_id, \"t\": session_data\[\"tenant_id\"\]\}\)\n\s+idx = idx_res\.fetchone\(\)\n\s+if idx:\n\s+xml_content = f\"<\?xml version='1\.0'\?><indice><hash_estado>\{idx\.firma_indice\}</hash_estado></indice>\" # Mock simple\n\s+zip_file\.writestr\(\"indice_electronico\.xml\", xml_content\))"

replacement = r"""# Obtener XML real
        exp_res = await db.execute(text("SELECT indice_xml_path FROM agn_expedientes WHERE id = :eid AND tenant_id = :t"), {"eid": expediente_id, "t": session_data["tenant_id"]})
        exp_row = exp_res.fetchone()
        if exp_row and exp_row.indice_xml_path and os.path.exists(exp_row.indice_xml_path):
            with open(exp_row.indice_xml_path, "r", encoding="utf-8") as xmlf:
                xml_content = xmlf.read()
            zip_file.writestr("indice_electronico.xml", xml_content)
        else:
            # Fallback a registro de base de datos
            idx_res = await db.execute(text("SELECT * FROM agn_indice_electronico WHERE expediente_id = :eid ORDER BY fecha_accion DESC LIMIT 1"), {"eid": expediente_id, "t": session_data["tenant_id"]})
            idx = idx_res.fetchone()
            if idx:
                xml_content = f"<?xml version='1.0'?><indice><hash_estado>{idx.firma_indice}</hash_estado></indice>"
                zip_file.writestr("indice_electronico.xml", xml_content)"""

new_agn = re.sub(pattern, replacement, agn)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(new_agn)
