with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for j in range(1690, 1720):
    print(f"{j}: {lines[j].strip()}")
