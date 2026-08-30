with open("app/templates/components/expedientes_module.html", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    '<input type="hidden" name="subserie_id" value="{{ subserie_id }}">',
    '<input type="hidden" name="serie_id" value="{{ serie_id|default(\'\') }}">\n        <input type="hidden" name="subserie_id" value="{{ subserie_id|default(\'\') }}">'
)

with open("app/templates/components/expedientes_module.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Added hidden serie_id")
