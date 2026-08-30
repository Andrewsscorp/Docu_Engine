with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if "def " in line and ("upload_direct" in line or "vincular" in line):
            print(f"Line {i}: {line.strip()}")
