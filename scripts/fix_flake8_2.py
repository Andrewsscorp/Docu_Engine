with open("app/routers/documents.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "session_data[\"tenant_id\"]" in line and i > 1440 and i < 1460:
        lines[i] = line.replace("session_data[\"tenant_id\"]", "tenant_id")
with open("app/routers/documents.py", "w", encoding="utf-8") as f:
    f.writelines(lines)

with open("app/rbac.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "global rbac_l1_cache" in line:
        lines[i] = ""
with open("app/rbac.py", "w", encoding="utf-8") as f:
    f.writelines(lines)

with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "from fastapi.templating import Jinja2Templates" in line and i > 1810 and i < 1820:
        lines[i] = "        from fastapi.templating import Jinja2Templates; templates = Jinja2Templates(directory='app/templates')\n        from fastapi import Request\n        req = locals().get('request', Request({'type': 'http'}))\n        return templates.TemplateResponse('components/trd_table.html', {'request': req, 'trds': context['trds']})\n"
with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.writelines(lines)
