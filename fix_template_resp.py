import re
with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace TemplateResponse arguments
old_resp = """return templates.TemplateResponse("pages/expediente_view.html", {"""
new_resp = """return templates.TemplateResponse(request=request, name="pages/expediente_view.html", context={"""
content = content.replace(old_resp, new_resp)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
