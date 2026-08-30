with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for j in range(2306, 2355):
    print(lines[j].strip())
