with open("tests/test_api_contratos.py", "r", encoding="latin-1") as f:
    content = f.read()

content = content.replace("excepcin", "excepción")
content = content.replace("autenticacin", "autenticación")

with open("tests/test_api_contratos.py", "w", encoding="utf-8") as f:
    f.write(content)
