with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i in range(max(0, 1645), min(len(lines), 1665)):
    print(f"{i+1}: {lines[i]}", end="")
