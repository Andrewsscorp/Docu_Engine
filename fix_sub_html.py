with open("app/templates/components/subseries_module.html", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    'hx-get="/api/v1/agn/expedientes/module?subserie_id={{ carpeta.id }}"',
    'hx-get="/api/v1/agn/expedientes/module?dummy=1{{ carpeta.filtro_id }}"'
)
content = content.replace(
    '{{ carpeta.subserie_nombre }}',
    '{{ carpeta.nombre_mostrar }}'
)

with open("app/templates/components/subseries_module.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated subseries_module.html")
