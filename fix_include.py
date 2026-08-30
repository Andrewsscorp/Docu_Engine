with open("app/templates/components/expedientes_grid_items.html", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    "[name='subserie_id']",
    "[name='serie_id'], [name='subserie_id']"
)

with open("app/templates/components/expedientes_grid_items.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated grid items include")
