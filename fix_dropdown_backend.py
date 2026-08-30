with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re
old_render = """    return templates.TemplateResponse(request=request, name="pages/expediente_view.html", context={
        "request": request,
        "exp": exp,
        "docs": docs,
        "eventos": eventos,
        "tipologias": tipologias,
        "user_docs": user_docs,
        "completitud_pct": completitud_pct,
        "completadas": completadas,
        "requeridas": requeridas
    })"""

new_render = """    dropdown_tipologias = [t for t in tipologias if t["obligatoria"] is False]
    return templates.TemplateResponse(request=request, name="pages/expediente_view.html", context={
        "request": request,
        "exp": exp,
        "docs": docs,
        "eventos": eventos,
        "tipologias": tipologias,
        "dropdown_tipologias": dropdown_tipologias,
        "user_docs": user_docs,
        "completitud_pct": completitud_pct,
        "completadas": completadas,
        "requeridas": requeridas
    })"""

if old_render in content:
    content = content.replace(old_render, new_render)
else:
    print("Old render not found")

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
