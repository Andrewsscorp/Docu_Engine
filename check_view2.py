with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for j in range(1720, 1740):
    print(f"{j}: {lines[j].strip()}")
