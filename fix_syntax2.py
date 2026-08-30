import re
with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

# Fix the broken string block
broken_pattern = r'csv_content = "NO_ORDEN,CODIGO,NOMBRE_UNIDAD,FECHA_INICIAL,FECHA_FINAL,CAJA_CARPETA,FOLIOS,SOPORTE\n"'
content = re.sub(broken_pattern, 'csv_content = "NO_ORDEN,CODIGO,NOMBRE_UNIDAD,FECHA_INICIAL,FECHA_FINAL,CAJA_CARPETA,FOLIOS,SOPORTE\\n"', content)

# But wait, let's see what is actually there.
