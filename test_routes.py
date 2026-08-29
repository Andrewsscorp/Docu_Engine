from app.main import app
for route in app.routes:
    if 'auth' in route.path:
        print(route.methods, route.path)
