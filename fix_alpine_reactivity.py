with open("app/templates/components/modal_vincular_trd.html", "r", encoding="utf-8") as f:
    content = f.read()

import re
old_push = r"this\.tipologias\.push\(data\.data\);\s*this\.tipologias\.sort\(\(a,b\) => a\.text\.localeCompare\(b\.text\)\);"
new_push = "this.tipologias = [...this.tipologias, data.data].sort((a,b) => a.text.localeCompare(b.text));"

content = re.sub(old_push, new_push, content)

with open("app/templates/components/modal_vincular_trd.html", "w", encoding="utf-8") as f:
    f.write(content)
