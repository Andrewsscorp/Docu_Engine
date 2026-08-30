with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

with open("exp_view_code.txt", "w", encoding="utf-8") as out:
    for i, line in enumerate(lines):
        if "def " in line and "view" in line.lower():
            out.write(f"Line {i}: {line.strip()}\n")
            for j in range(i, i+60):
                if j < len(lines):
                    out.write(lines[j])
            out.write("---\n")
