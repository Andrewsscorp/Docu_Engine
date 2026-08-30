with open("app/routers/documents.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for j in range(1290, 1315):
    print(lines[j].strip())
