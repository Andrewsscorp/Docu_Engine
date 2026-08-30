with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    for line in lines:
        if 'csv_content = "NO_ORDEN' in line and not line.strip().endswith('n"'):
            f.write('    csv_content = "NO_ORDEN,CODIGO,NOMBRE_UNIDAD,FECHA_INICIAL,FECHA_FINAL,CAJA_CARPETA,FOLIOS,SOPORTE\\n"\n')
        else:
            f.write(line)
