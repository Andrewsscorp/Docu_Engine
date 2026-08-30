with open("app/routers/documents.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for j in range(330, 360):
    if j < len(lines):
        print(f"Line {j}: {lines[j].strip()}")
