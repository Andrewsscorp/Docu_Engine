with open("tests/test_inmutabilidad_ciclo.py", "r", encoding="latin-1") as f:
    content = f.read()

content = content.replace("edicin", "edición")
content = content.replace("auditora", "auditoría")
content = content.replace("excepcin", "excepción")
content = content.replace("manipulacin", "manipulación")
content = content.replace("diseo", "diseño")
content = content.replace("Lgica", "Lógica")

with open("tests/test_inmutabilidad_ciclo.py", "w", encoding="utf-8") as f:
    f.write(content)
