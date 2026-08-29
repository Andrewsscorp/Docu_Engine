with open('app/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

if "from app.routers import agn" not in content:
    content = content.replace(
        "from app.routers import auth, documents, rbac, configuracion, buzon, etiquetas, tareas",
        "from app.routers import auth, documents, rbac, configuracion, buzon, etiquetas, tareas, agn"
    )
    content = content.replace(
        "app.include_router(tareas.router)",
        "app.include_router(tareas.router)\napp.include_router(agn.router)"
    )
    with open('app/main.py', 'w', encoding='utf-8') as f:
        f.write(content)
