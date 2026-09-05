import re

with open("app/main.py", "r", encoding="utf-8") as f:
    main_code = f.read()

# Replace the catch_exceptions_middleware to log the exception
old_middleware = """@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        return HTMLResponse(f"<div class='text-red-500 font-bold'>CSRF Error: {e}</div>", status_code=200)"""

new_middleware = """@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Excepcion no controlada en ruta {request.url.path}: {str(e)}", exc_info=True)
        return HTMLResponse(f"<div class='text-red-500 font-bold'>Error Interno del Servidor. Contacte al Administrador.</div>", status_code=500)"""

if "logger.error(f\"Excepcion no controlada" not in main_code:
    main_code = main_code.replace(old_middleware, new_middleware)

with open("app/main.py", "w", encoding="utf-8") as f:
    f.write(main_code)
