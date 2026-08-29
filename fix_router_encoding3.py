with open('app/routers/agn.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re
content = re.sub(r'ELECTR.NICO', 'ELECTRÓNICO', content)
content = re.sub(r'Secci.n', 'Sección', content)
content = re.sub(r'Subsecci.n', 'Subsección', content)
content = re.sub(r'pr.ximamente', 'próximamente', content)

with open('app/routers/agn.py', 'w', encoding='utf-8') as f:
    f.write(content)
