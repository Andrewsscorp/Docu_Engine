with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

old_return = """    return templates.TemplateResponse("pages/fuid_view.html", {
        "request": request,
        "subserie": subserie,
        "registros": registros
    })"""

new_return = """    subserie_dict = dict(subserie._mapping) if subserie else {}
    return templates.TemplateResponse(request=request, name="pages/fuid_view.html", context={
        "request": request,
        "subserie": subserie_dict,
        "registros": registros
    })"""

content = content.replace(old_return, new_return)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
