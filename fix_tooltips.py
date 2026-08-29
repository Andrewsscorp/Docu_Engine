with open('app/routers/agn.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Fondo ?
content = re.sub(r'Ayuda prximamente', 'Entidad productora u organismo que ha reunido o generado los documentos.', content, count=1)
content = re.sub(r'Ayuda próximamente', 'Entidad productora u organismo que ha reunido o generado los documentos.', content, count=1)

# Sección ?
content = re.sub(r'Ayuda prximamente', 'Dependencia administrativa de alto nivel (ej. Dirección, Secretaría).', content, count=1)
content = re.sub(r'Ayuda próximamente', 'Dependencia administrativa de alto nivel (ej. Dirección, Secretaría).', content, count=1)

# Subsección ?
content = re.sub(r'Ayuda prximamente', 'Unidad administrativa operativa o grupo de trabajo subordinado.', content, count=1)
content = re.sub(r'Ayuda próximamente', 'Unidad administrativa operativa o grupo de trabajo subordinado.', content, count=1)

# Serie ?
content = re.sub(r'Ayuda prximamente', 'Conjunto de expedientes con estructura y contenido homogéneos.', content, count=1)
content = re.sub(r'Ayuda próximamente', 'Conjunto de expedientes con estructura y contenido homogéneos.', content, count=1)

# Subserie ?
content = re.sub(r'Ayuda prximamente', 'División de la serie documental según un trámite específico.', content, count=1)
content = re.sub(r'Ayuda próximamente', 'División de la serie documental según un trámite específico.', content, count=1)

with open('app/routers/agn.py', 'w', encoding='utf-8') as f:
    f.write(content)
