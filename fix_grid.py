with open("app/templates/components/expedientes_grid.html", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("{% if not expedientes and page == 1 %}", "{% if not expedientes and not is_append %}")

with open("app/templates/components/expedientes_grid.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated expedientes_grid.html")
