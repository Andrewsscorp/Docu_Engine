with open("app/main.py", "r", encoding="utf-8") as f:
    main_code = f.read()

main_code = main_code.replace(
    'app = FastAPI(title="DocuEngine Backend", version="1.0.0")',
    'app = FastAPI(title="DocuEngine Backend", version="1.0.0", docs_url=None, redoc_url=None, openapi_url=None)'
)

with open("app/main.py", "w", encoding="utf-8") as f:
    f.write(main_code)
