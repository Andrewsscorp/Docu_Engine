with open("tests/test_dominio_archivistico.py", "r", encoding="latin-1") as f:
    content = f.read()

# Fix encoding artifacts
content = content.replace("invǭlida", "inválida")
content = content.replace("Tipologas", "Tipologías")
content = content.replace("tipologa", "tipología")
content = content.replace("Transicin", "Transición")

with open("tests/test_dominio_archivistico.py", "w", encoding="utf-8") as f:
    f.write(content)
