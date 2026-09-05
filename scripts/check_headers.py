with open("app/main.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if "response.headers" in line or "add_hsts_header" in line or "CORSMiddleware" in line:
            print(f"Line {i+1}: {line.strip()}")
