with open("app/main.py", "r", encoding="utf-8") as f:
    content = f.read()

if "from app.routers.agn_tree import tree_router" not in content:
    content = content.replace(
        "from app.routers import auth, documents, agn", 
        "from app.routers import auth, documents, agn\nfrom app.routers.agn_tree import tree_router"
    )
    content = content.replace(
        "app.include_router(agn.router)",
        "app.include_router(agn.router)\napp.include_router(tree_router)"
    )
    with open("app/main.py", "w", encoding="utf-8") as f:
        f.write(content)
