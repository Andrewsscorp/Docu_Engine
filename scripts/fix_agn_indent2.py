with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    for i, line in enumerate(lines):
        if "from fastapi import Request" in line and i > 1800 and i < 1820:
            continue
        f.write(line)
