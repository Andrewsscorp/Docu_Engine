with open('app/routers/agn.py', 'r', encoding='utf-8') as f:
    content = f.read()
import re
match = re.search(r'<form id="crear-fondo-form"[\s\S]*?</form>', content)
if match:
    print(match.group(0))
else:
    print("Not found")
