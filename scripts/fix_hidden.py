with open("app/templates/components/explorer.html", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("value=\"\">", "value=\"{{ agn_expediente_id }}\">")

with open("app/templates/components/explorer.html", "w", encoding="utf-8") as f:
    f.write(content)
