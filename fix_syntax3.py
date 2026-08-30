with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    for line in lines:
        if line.strip() == '"':
            continue
        f.write(line)
