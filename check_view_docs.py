with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for j in range(1665, 1690):
    print(lines[j].strip())
