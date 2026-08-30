with open("expediente_view_old.html", "r", encoding="utf-16") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "Documentos PDF <span class=" in line:
        start_idx = i - 2
        print("Found at line", i)
        print("".join(lines[start_idx:start_idx+12]))
        break
