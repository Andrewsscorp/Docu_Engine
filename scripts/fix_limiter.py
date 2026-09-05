with open("app/main.py", "r", encoding="utf-8") as f:
    main_code = f.read()

setup_str = """
app = FastAPI(title="DocuEngine Backend", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
"""
if "app.state.limiter = limiter" not in main_code:
    main_code = main_code.replace('app = FastAPI(title="DocuEngine Backend", version="1.0.0")', setup_str)

with open("app/main.py", "w", encoding="utf-8") as f:
    f.write(main_code)
