with open("app/templates/pages/control_tipologias.html", "r", encoding="utf-8") as f:
    content = f.read()

import re
old_button = r'<button hx-post="/api/v1/agn/expedientes/\{\{ exp\.id \}\}/cerrar" hx-swap="none" class="w-full py-3 bg-green-500 hover:bg-green-600 text-white rounded-xl font-bold transition-colors">\s*Sellar Expediente 100%\s*</button>'
new_button = """<button type="button" onclick="cerrarExpediente()" class="w-full py-3 bg-green-500 hover:bg-green-600 text-white rounded-xl font-bold transition-colors">
                        Sellar Expediente 100%
                    </button>"""

content = re.sub(old_button, new_button, content)

with open("app/templates/pages/control_tipologias.html", "w", encoding="utf-8") as f:
    f.write(content)
