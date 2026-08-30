with open("app/templates/pages/dashboard.html", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i, line in enumerate(lines[-30:]):
    print(f"Line {len(lines) - 30 + i}: {line.strip()}")
