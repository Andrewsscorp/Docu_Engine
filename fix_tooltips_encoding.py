with open('app/routers/agn.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re

fixes = {
    r'Identificador alfanum.rico .nico': 'Identificador alfanumérico único',
    r'Raz.n social legal y completa de la instituci.n': 'Razón social legal y completa de la institución',
    r'Resoluci.n, Decreto, etc.': 'Resolución, Decreto, etc.',
    r'resoluci.n que crea': 'resolución que crea',
    r'Condici.n activa': 'Condición activa',
    r'C.digo Oficial del Fondo': 'Código Oficial del Fondo'
}

for k, v in fixes.items():
    content = re.sub(k, v, content)

with open('app/routers/agn.py', 'w', encoding='utf-8') as f:
    f.write(content)
