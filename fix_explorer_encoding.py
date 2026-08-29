with open('app/templates/components/explorer.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
content = re.sub(r'Entidades P.blicas', 'Entidades Públicas', content)

with open('app/templates/components/explorer.html', 'w', encoding='utf-8') as f:
    f.write(content)
