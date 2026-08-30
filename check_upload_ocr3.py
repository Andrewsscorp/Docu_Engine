with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for j in range(2380, 2400):
    if j < len(lines):
        print(lines[j].strip())
