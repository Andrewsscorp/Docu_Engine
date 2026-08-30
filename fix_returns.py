with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re
match = re.search(r'return templates\.TemplateResponse\("pages/expedientes_module\.html".*?\}\)', content, re.DOTALL)

if match:
    new_return = """context = {
        "request": request, 
        "expedientes": expedientes,
        "subseries": subseries,
        "total_count": total_count,
        "has_more": len(expedientes) == limit,
        "q": q, "status": status, "subserie_id": subserie_id,
        "fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin, "soporte": soporte,
        "is_append": bool(ultimo_id)
    }
    
    # HTMX Target Check
    if request.headers.get("hx-target") == "expedientes-results-grid" or request.headers.get("hx-target") == "expedientes-append-target":
        template_name = "components/expedientes_grid_items.html" if request.headers.get("hx-target") == "expedientes-append-target" else "components/expedientes_grid.html"
        return templates.TemplateResponse(request=request, name=template_name, context=context)
        
    return templates.TemplateResponse(request=request, name="components/expedientes_module.html", context=context)"""
    
    content = content.replace(match.group(0), new_return)
    with open("app/routers/agn.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Fixed endpoint returns.")
else:
    print("Could not find return block")
