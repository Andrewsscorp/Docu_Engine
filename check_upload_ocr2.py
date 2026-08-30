with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for j in range(2355, 2380):
    print(lines[j].strip())
