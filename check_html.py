with open("app/templates/pages/expediente_view.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "x-show" in line or "@click" in line or "x-model" in line or "x-bind" in line:
        # Check for unescaped characters or bad syntax
        if "\\" in line:
            print(f"Line {i+1} has backslashes: {line.strip()}")
        # Check for matching quotes very simply
        if line.count("'") % 2 != 0:
            print(f"Line {i+1} has uneven single quotes: {line.strip()}")
        if line.count('"') % 2 != 0:
            print(f"Line {i+1} has uneven double quotes: {line.strip()}")

