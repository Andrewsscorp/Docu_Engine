with open("app/templates/components/expedientes_module.html", "r", encoding="utf-8") as f:
    content = f.read()

# Replace Header
header_old = """        <div>
            <h1 class="text-[28px] font-bold text-gray-900 leading-tight flex items-center gap-3">
                Gestin de Expedientes 
                <span id="total-expedientes-badge" class="text-sm font-semibold bg-gray-100 text-gray-500 px-3 py-1 rounded-full border border-gray-200">
                    {{ total_count|default(0) }} Total
                </span>
            </h1>
        </div>"""

header_new = """        <div class="flex flex-col gap-2">
            {% if breadcrumb %}
            <nav class="flex text-sm text-gray-500 font-medium" aria-label="Breadcrumb">
              <ol class="inline-flex items-center space-x-1 md:space-x-3">
                <li class="inline-flex items-center">
                  <a href="#" hx-get="/api/v1/agn/expedientes/module" hx-target="closest section" class="inline-flex items-center hover:text-indigo-600 transition-colors">
                    <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20"><path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"></path></svg>
                    TRD
                  </a>
                </li>
                {% set parts = breadcrumb.split(" > ") %}
                {% for part in parts %}
                {% if not loop.first %}
                <li>
                  <div class="flex items-center">
                    <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                    <span class="ml-1 md:ml-2 text-gray-700 font-bold">{{ part }}</span>
                  </div>
                </li>
                {% endif %}
                {% endfor %}
              </ol>
            </nav>
            {% else %}
            <h1 class="text-[28px] font-bold text-gray-900 leading-tight flex items-center gap-3">
                Gestin de Expedientes 
                <span id="total-expedientes-badge" class="text-sm font-semibold bg-gray-100 text-gray-500 px-3 py-1 rounded-full border border-gray-200">
                    {{ total_count|default(0) }} Total
                </span>
            </h1>
            {% endif %}
        </div>"""

if header_old in content:
    content = content.replace(header_old, header_new)
else:
    # Use regex
    import re
    content = re.sub(r'<div>\s*<h1 class="text-\[28px\].*?</h1>\s*</div>', header_new, content, flags=re.DOTALL)

# Hide Subserie select if breadcrumb is present
select_sub = """<select name="subserie_id" class="h-[42px] bg-white border border-gray-200 text-gray-700 text-sm font-medium rounded-xl focus:ring-primary focus:border-primary block px-3 shadow-sm min-w-[180px] max-w-[240px] outline-none truncate" title="Filtrar por Subserie">"""

select_sub_new = """{% if breadcrumb %}
        <input type="hidden" name="subserie_id" value="{{ subserie_id }}">
        {% else %}
        <select name="subserie_id" class="h-[42px] bg-white border border-gray-200 text-gray-700 text-sm font-medium rounded-xl focus:ring-primary focus:border-primary block px-3 shadow-sm min-w-[180px] max-w-[240px] outline-none truncate" title="Filtrar por Subserie">
            <option value="">Serie / Subserie</option>
            {% for sub in subseries %}
            <option value="{{ sub.id }}" {% if subserie_id == sub.id|string %}selected{% endif %}>{{ sub.codigo }} - {{ sub.nombre }}</option>
            {% endfor %}
        </select>
        {% endif %}
        <!-- HIDDEN REPLACEMENT ANCHOR -->"""

# We just replace the <select block
import re
content = re.sub(r'<select name="subserie_id".*?</select>', select_sub_new, content, flags=re.DOTALL)


with open("app/templates/components/expedientes_module.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated expedientes_module.html")
