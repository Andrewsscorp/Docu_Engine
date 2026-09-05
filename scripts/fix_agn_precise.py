with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if i == 1811:
        lines[i] = "        from fastapi.templating import Jinja2Templates; templates = Jinja2Templates(directory='app/templates'); from fastapi import Request; req = locals().get('request', Request({'type': 'http'}))\n        return templates.TemplateResponse('components/trd_table.html', {'request': req, 'trds': context['trds'] if 'context' in locals() else []})\n"
    elif i == 2624:
        lines[i] = line.replace("expediente_id", "exp_id")

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.writelines(lines)
