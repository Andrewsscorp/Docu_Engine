with open("app/main.py", "r", encoding="utf-8") as f:
    content = f.read()

middleware = """
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import traceback

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    import logging
    logging.error(f"422 Error at {request.url}")
    logging.error(f"Body: {await request.body()}")
    logging.error(f"Validation error details: {exc.errors()}")
    with open("422_debug.log", "w", encoding="utf-8") as lf:
        lf.write(f"URL: {request.url}\n")
        lf.write(f"Errors: {exc.errors()}\n")
    return JSONResponse(status_code=422, content={"detail": exc.errors()})
"""

# Insert right after `app = FastAPI(...)`
import re
content = re.sub(r'(app = FastAPI[^\n]*\n)', r'\1' + middleware, content)

with open("app/main.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Added 422 logger middleware")
