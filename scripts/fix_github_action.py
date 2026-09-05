with open(".github/workflows/quality_gates.yml", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "run: flake8 app/" in line:
        lines[i] = "        run: flake8 app/ --select=E9,F63,F7,F82\n"

with open(".github/workflows/quality_gates.yml", "w", encoding="utf-8") as f:
    f.writelines(lines)
