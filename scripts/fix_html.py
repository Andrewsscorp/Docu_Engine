with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re
match = re.search(r'@router\.get\("/modal/fondo"\).*?html = f"""(.*?)"""', content, re.DOTALL)
if match:
    html = match.group(1).replace("{{", "{").replace("}}", "}")
    with open("app/templates/modals/crear_fondo.html", "w", encoding="utf-8") as f:
        f.write(html)
        print("Success")
else:
    print("Not found")
