with open("app/templates/pages/dashboard.html", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('name="archivo"', 'name="file"')

with open("app/templates/pages/dashboard.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed input name in dashboard")
