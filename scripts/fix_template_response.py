with open("app/routers/agn_tree.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    'return templates.TemplateResponse("components/agn_tree.html", {"request": request, "tree": root_nodes})',
    'return templates.TemplateResponse(request=request, name="components/agn_tree.html", context={"request": request, "tree": root_nodes})'
)

with open("app/routers/agn_tree.py", "w", encoding="utf-8") as f:
    f.write(content)
