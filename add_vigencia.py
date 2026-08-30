with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

from datetime import datetime
current_year = datetime.now().year

content = content.replace(
    'breadcrumb = f"Fondo > {bc[\'dep_nombre\']} > {bc[\'serie_nombre\']} > {bc[\'subserie_nombre\']}"',
    'import datetime\nbreadcrumb = f"Fondo > {bc[\'dep_nombre\']} > {bc[\'serie_nombre\']} > {bc[\'subserie_nombre\']} > Vigencia {datetime.datetime.now().year}"'
)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated breadcrumb to include Vigencia")
