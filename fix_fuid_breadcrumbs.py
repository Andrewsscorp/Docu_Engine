with open("app/templates/pages/fuid_view.html", "r", encoding="utf-8") as f:
    content = f.read()

import re

# We want to replace the Reportes span with a clickable one
old_reportes = """<span class="inline-flex items-center hover:text-indigo-600 transition-colors cursor-pointer">Reportes</span>"""

new_reportes = """{% if expediente_id_origen %}
<span hx-get="/api/v1/agn/expedientes/{{ expediente_id_origen }}/view" hx-target="#expediente-inner-container" class="inline-flex items-center hover:text-indigo-600 transition-colors cursor-pointer text-indigo-500 font-medium tooltip" title="Volver al Expediente">Expediente Origen</span>
{% else %}
<span class="inline-flex items-center hover:text-indigo-600 transition-colors cursor-pointer">Reportes</span>
{% endif %}"""

content = content.replace(old_reportes, new_reportes)

with open("app/templates/pages/fuid_view.html", "w", encoding="utf-8") as f:
    f.write(content)
