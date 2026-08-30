with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

bad_str = """        return templates.TemplateResponse("components/subseries_module.html", {
            "request": request,
            "carpetas": carpetas,
            "total_folders": total_folders
        })"""

good_str = """        return templates.TemplateResponse(request=request, name="components/subseries_module.html", context={
            "request": request,
            "carpetas": carpetas,
            "total_folders": total_folders
        })"""

if bad_str in content:
    content = content.replace(bad_str, good_str)
    with open("app/routers/agn.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Fixed TemplateResponse syntax")
else:
    print("Could not find bad_str")
