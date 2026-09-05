with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    for line in lines:
        if "from fastapi.templating import Jinja2Templates; templates =" in line: continue
        if "from fastapi import Request" in line and "req = locals().get" not in line: 
            f.write(line)
            continue
        if "req = locals().get('request'" in line: continue
        if "return templates.TemplateResponse('components/trd_table.html'" in line: continue
        if "# Full module response" in line: continue
        f.write(line)
