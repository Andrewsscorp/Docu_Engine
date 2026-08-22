with open("app/main.py", "r", encoding="utf-8") as f:
    content = f.read()

if "from app.routers import notifications" not in content:
    content = content.replace(
        "from app.routers import auth, documents, rbac, settings, editor",
        "from app.routers import auth, documents, rbac, settings, editor, notifications"
    )
    
    content = content.replace(
        "app.include_router(editor.router)",
        "app.include_router(editor.router)\napp.include_router(notifications.router)"
    )
    
    with open("app/main.py", "w", encoding="utf-8") as f:
        f.write(content)
        print("Included notifications router in main.py")
