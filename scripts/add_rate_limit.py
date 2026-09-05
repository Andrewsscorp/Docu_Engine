with open("app/main.py", "r", encoding="utf-8") as f:
    main_code = f.read()

# Add slowapi imports
import_str = """
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])
"""

if "from slowapi" not in main_code:
    main_code = main_code.replace("from fastapi import FastAPI, Request", import_str + "\nfrom fastapi import FastAPI, Request")
    
    # Add exception handler and state
    setup_str = """
app = FastAPI(title="DocuEngine SGDEA", docs_url=None, redoc_url=None)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
"""
    main_code = main_code.replace("app = FastAPI(title=\"DocuEngine SGDEA\", docs_url=None, redoc_url=None)", setup_str)
    
with open("app/main.py", "w", encoding="utf-8") as f:
    f.write(main_code)
