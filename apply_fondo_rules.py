with open('app/routers/agn.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Update Fondo query in the Expediente modal to filter by ABIERTO
content = re.sub(
    r"WHERE tipo = 'FONDO' AND tenant_id = :t",
    r"WHERE tipo = 'FONDO' AND estado = 'ABIERTO' AND tenant_id = :t",
    content
)

# Update the dropdown in the Crear Fondo modal
old_options = '''<option value="ACTIVA">Fondo Abierto / Activo</option>
                        <option value="FUSIONADA">Fondo Fusionado</option>
                        <option value="SUPRIMIDA">Fondo Suprimido / Cerrado</option>'''
new_options = '''<option value="ABIERTO">Fondo Abierto (Activo)</option>
                        <option value="CERRADO">Fondo Cerrado (Acumulado)</option>'''
content = content.replace(old_options, new_options)

with open('app/routers/agn.py', 'w', encoding='utf-8') as f:
    f.write(content)
