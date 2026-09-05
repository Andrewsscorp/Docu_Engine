with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
# Fix undefined request and templates
for i, line in enumerate(lines):
    if "templates.TemplateResponse" in line and i > 1800 and i < 1820:
        lines[i] = "        from fastapi.templating import Jinja2Templates; templates = Jinja2Templates(directory='app/templates')\n        return templates.TemplateResponse('components/trd_table.html', {'request': request if 'request' in locals() else {}, 'trds': context['trds']})\n"
    if "expediente_id" in line and i > 2610:
        lines[i] = line.replace("expediente_id", "''")

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.writelines(lines)
