with open("app/templates/pages/fuid_view.html", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('hx-target="#dashboard-main-container"', 'hx-target="#expediente-inner-container"')

with open("app/templates/pages/fuid_view.html", "w", encoding="utf-8") as f:
    f.write(content)
