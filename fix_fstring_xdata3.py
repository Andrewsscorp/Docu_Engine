with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("x-data=\"{ fileName: '' }\"", "x-data=\"{{ fileName: '' }}\"")

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
