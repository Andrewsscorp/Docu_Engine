with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    for i, line in enumerate(lines):
        if i >= 1810 and i <= 1812:
            continue
        f.write(line)
