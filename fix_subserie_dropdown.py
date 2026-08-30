with open("app/templates/components/expedientes_module.html", "r", encoding="utf-8") as f:
    content = f.read()

import re

old_select = """        <!-- TRD (Mockup placeholder, dynamic load requires more endpoints) -->
        <select name="subserie_id" class="bg-white border border-gray-200 text-gray-700 text-sm font-medium rounded-xl focus:ring-primary focus:border-primary block p-2.5 shadow-sm min-w-[160px] outline-none">
            <option value="">Serie / Subserie</option>
            <!-- Needs to be populated by backend or API -->
        </select>"""

new_select = """        <select name="subserie_id" class="bg-white border border-gray-200 text-gray-700 text-sm font-medium rounded-xl focus:ring-primary focus:border-primary block p-2.5 shadow-sm min-w-[160px] max-w-[200px] outline-none truncate" title="Filtrar por Subserie">
            <option value="">Serie / Subserie</option>
            {% for sub in subseries %}
            <option value="{{ sub.id }}" {% if subserie_id == sub.id|string %}selected{% endif %}>{{ sub.codigo }} - {{ sub.nombre }}</option>
            {% endfor %}
        </select>"""

content = content.replace(old_select, new_select)

with open("app/templates/components/expedientes_module.html", "w", encoding="utf-8") as f:
    f.write(content)
