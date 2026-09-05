import json

with open("inventory_baseline.json", "r") as f:
    data = json.load(f)
    
md = "# Inventario de Línea Base (Fase 0)\n\n"
md += "## Tablas de Base de Datos\n"
for t in sorted(data["tables"]):
    md += f"- `{t}`\n"
    
md += "\n## Endpoints del API\n"
for e in sorted(data["endpoints"]):
    md += f"- `{e}`\n"

with open("inventory_baseline.md", "w", encoding="utf-8") as f:
    f.write(md)
