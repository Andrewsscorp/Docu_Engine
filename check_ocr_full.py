with open("app/routers/documents.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for j in range(150, 190):
    if j < len(lines):
        print(lines[j].strip())
