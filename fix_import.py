with open('app/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    "from app.routers import auth, rbac, documents, settings, editor, notifications, etiquetas, tareas",
    "from app.routers import auth, rbac, documents, settings, editor, notifications, etiquetas, tareas, agn"
)

with open('app/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
