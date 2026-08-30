with open("app/templates/pages/expediente_view.html", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('hx-push-url="true"', '')

with open("app/templates/pages/expediente_view.html", "w", encoding="utf-8") as f:
    f.write(content)
