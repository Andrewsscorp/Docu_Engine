with open('app/routers/agn.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# We can replace the broken words using regex!
content = re.sub(r'Clasificaci.n', 'Clasificación', content)
content = re.sub(r'ELECTR.NICO', 'ELECTRÓNICO', content)
content = re.sub(r'Secci.n', 'Sección', content)
content = re.sub(r'Subsecci.n', 'Subsección', content)
content = re.sub(r'Autom.ticamente', 'Automáticamente', content)
content = re.sub(r'Identificaci.n', 'Identificación', content)

with open('app/routers/agn.py', 'w', encoding='utf-8') as f:
    f.write(content)
