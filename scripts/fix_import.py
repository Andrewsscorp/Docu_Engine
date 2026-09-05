with open("app/main.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    "from app.routers import auth, rbac, documents, settings, editor, notifications, etiquetas, tareas, agn", 
    "from app.routers import auth, rbac, documents, settings, editor, notifications, etiquetas, tareas, agn\nfrom app.routers.agn_tree import tree_router"
)

with open("app/main.py", "w", encoding="utf-8") as f:
    f.write(content)
