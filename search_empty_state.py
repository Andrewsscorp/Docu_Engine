with open("app/templates/pages/control_tipologias.html", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "Matriz TRD Vac" in line or "Parametrizar Reglas TRD Ahora" in line or "Parametrizar TRD" in line:
        print(f"Line {i}: {line.strip()}")
        # print some context
        for j in range(max(0, i-2), min(len(lines), i+3)):
            print(f"  {j}: {lines[j].strip()}")
