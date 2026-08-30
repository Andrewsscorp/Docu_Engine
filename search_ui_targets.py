with open("app/templates/pages/control_tipologias.html", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "Heredar de Subserie" in line or "Cargar Documento" in line or "CARGADO" in line:
        print(f"Line {i}: {line.strip()}")
