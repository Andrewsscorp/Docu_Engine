with open("app/templates/pages/expediente_view.html", "r", encoding="utf-8") as f:
    content = f.read()

import re
old_show = r"filtroDoc === \\'\\' \|\| \\'\{\{ doc\.file_name \| lower \}\} \{\{ doc\.tipo_nombre \| lower \}\}\\'.includes\(filtroDoc.toLowerCase\(\)\)"
new_show = "filtroDoc === '' || '{{ doc.file_name | lower }} {{ doc.tipo_nombre | lower }}'.includes(filtroDoc.toLowerCase())"

content = re.sub(old_show, new_show, content)

with open("app/templates/pages/expediente_view.html", "w", encoding="utf-8") as f:
    f.write(content)
