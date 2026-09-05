with open("tests/test_caos_resiliencia.py", "r", encoding="latin-1") as f:
    content = f.read()

content = content.replace("cada", "caída")

with open("tests/test_caos_resiliencia.py", "w", encoding="utf-8") as f:
    f.write(content)
