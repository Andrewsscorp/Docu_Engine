import re
with open("app/templates/pages/expediente_view.html", "r", encoding="utf-8") as f:
    content = f.read()

pattern = re.compile(r'<option value="">-- Seleccionar Tipo --</option>\s*{% for tip in tipologias %}\s*<option value="\{\{ tip\.id \}\}">\{\{ tip\.nombre_oficial \}\}.*?</option>\s*{% endfor %}')

new_str = """<option value="">-- Seleccionar Tipo --</option>
                        <option value="ANEXO">Archivo Adjunto / Anexo</option>
                        {% for tip in dropdown_tipologias %}
                        <option value="{{ tip.id }}">{{ tip.nombre_oficial }}</option>
                        {% endfor %}"""

if pattern.search(content):
    content = pattern.sub(new_str, content)
    with open("app/templates/pages/expediente_view.html", "w", encoding="utf-8") as f:
        f.write(content)
        print("Dropdown Replaced!")
else:
    print("Not found by regex")
