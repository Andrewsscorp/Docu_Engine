with open("app/templates/pages/expediente_view.html", "r", encoding="utf-8") as f:
    content = f.read()

import re

# We want to replace the single button with a flex group
old_block_pattern = r'<div class="flex justify-between items-center">\s*<button \{% if exp\.estado_abierto %\}@click="addDocModal = true"\{% else %\}disabled\{% endif %\} class="bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 text-white font-bold py-2\.5 px-6 rounded-xl shadow-md transition-all flex items-center gap-2">\s*<svg[^>]*>.*?<\/svg>\s*Nuevo Documento\s*<\/button>\s*<\/div>'

new_block = """<div class="flex justify-between items-center">
                <div class="flex items-center gap-3">
                    <button hx-get="/api/v1/agn/expedientes/{{ exp.id }}/control_tipologias" hx-target="#expediente-inner-container" class="px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-xl transition-colors flex items-center gap-2 shadow-lg shadow-slate-200">
                        <svg class="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path></svg>
                        Control TRD
                    </button>
                    <button {% if exp.estado_abierto %}@click="addDocModal = true"{% else %}disabled{% endif %} class="bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 text-white font-bold py-2.5 px-6 rounded-xl shadow-md transition-all flex items-center gap-2">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                        Nuevo Documento
                    </button>
                </div>
            </div>"""

content = re.sub(old_block_pattern, new_block, content, flags=re.DOTALL)

with open("app/templates/pages/expediente_view.html", "w", encoding="utf-8") as f:
    f.write(content)
