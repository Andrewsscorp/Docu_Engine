with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re

# Remove Vigencia for Subserie
content = re.sub(
    r'import datetime\s+breadcrumb = f"Fondo > \{bc\[\'dep_nombre\'\]\} > \{bc\[\'serie_nombre\'\]\} > \{bc\[\'subserie_nombre\'\]\} > Vigencia \{datetime\.datetime\.now\(\)\.year\}"',
    'breadcrumb = f"Fondo > {bc[\'dep_nombre\']} > {bc[\'serie_nombre\']} > {bc[\'subserie_nombre\']}"',
    content
)

# Remove Vigencia for Serie
content = re.sub(
    r'import datetime\s+breadcrumb = f"Fondo > \{bc\[\'dep_nombre\'\]\} > \{bc\[\'serie_nombre\'\]\} > Vigencia \{datetime\.datetime\.now\(\)\.year\}"',
    'breadcrumb = f"Fondo > {bc[\'dep_nombre\']} > {bc[\'serie_nombre\']}"',
    content
)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Removed Vigencia from breadcrumbs")
