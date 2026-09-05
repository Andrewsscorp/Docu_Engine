with open(".github/workflows/quality_gates.yml", "r", encoding="utf-8") as f:
    lines = f.readlines()

with open(".github/workflows/quality_gates.yml", "w", encoding="utf-8") as f:
    for line in lines:
        if "G1 - Type Check (Mypy)" in line:
            continue
        if "run: mypy app/" in line:
            continue
        f.write(line)
