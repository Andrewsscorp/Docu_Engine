with open("app/templates/pages/fuid_view.html", "r", encoding="utf-8") as f:
    content = f.read()

import re

# Let's replace the first breadcrumb area completely
old_bc = """<li class="inline-flex items-center">
                    {% if expediente_id_origen %}
<span hx-get="/api/v1/agn/expedientes/{{ expediente_id_origen }}/view" hx-target="#expediente-inner-container" class="inline-flex items-center hover:text-indigo-600 transition-colors cursor-pointer text-indigo-500 font-medium tooltip" title="Volver al Expediente">Expediente Origen</span>
{% else %}
<span class="inline-flex items-center hover:text-indigo-600 transition-colors cursor-pointer">Reportes</span>
{% endif %}
                </li>
                <li>
                    <div class="flex items-center">
                        <svg class="w-4 h-4 text-slate-400 mx-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                        <span class="hover:text-indigo-600 transition-colors cursor-pointer">FUID</span>
                    </div>
                </li>"""

new_bc = """<li class="inline-flex items-center">
                    {% if expediente_id_origen %}
                    <button hx-get="/api/v1/agn/expedientes/{{ expediente_id_origen }}/view" hx-target="#expediente-inner-container" class="inline-flex items-center text-indigo-600 hover:text-indigo-800 transition-colors cursor-pointer font-bold bg-indigo-50 px-3 py-1.5 rounded-lg border border-indigo-100">
                        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
                        Volver al Expediente
                    </button>
                    {% else %}
                    <button onclick="window.location.href='/dashboard'" class="inline-flex items-center text-indigo-600 hover:text-indigo-800 transition-colors cursor-pointer font-bold bg-indigo-50 px-3 py-1.5 rounded-lg border border-indigo-100">
                        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path></svg>
                        Ir al Explorador
                    </button>
                    {% endif %}
                </li>"""

content = content.replace(old_bc, new_bc)

with open("app/templates/pages/fuid_view.html", "w", encoding="utf-8") as f:
    f.write(content)
