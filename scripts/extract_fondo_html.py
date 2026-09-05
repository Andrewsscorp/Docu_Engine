with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

html_str = []
in_html = False
for line in lines:
    if "@router.get(\"/modal/fondo\")" in line:
        pass
    if "html = f\"\"\"" in line:
        in_html = True
        continue
    if in_html and '"""' in line:
        in_html = False
        break
    if in_html:
        html_str.append(line)

import os
os.makedirs("app/templates/modals", exist_ok=True)
html_content = "".join(html_str).replace("{{", "{").replace("}}", "}")

with open("app/templates/modals/crear_fondo.html", "w", encoding="utf-8") as f:
    f.write(html_content)
