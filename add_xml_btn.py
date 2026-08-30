with open("app/templates/pages/expediente_view.html", "r", encoding="utf-8") as f:
    content = f.read()

import re
old_block = """                          <div class="bg-slate-50 group-hover:bg-white p-2 rounded-lg border border-slate-200 font-mono text-[10px] text-slate-400 break-all transition-colors">
                              Tx: {{ ev.firma_indice }}
                          </div>"""

new_block = """                          <div class="bg-slate-50 group-hover:bg-white p-2 rounded-lg border border-slate-200 font-mono text-[10px] text-slate-400 break-all transition-colors">
                              Tx: {{ ev.firma_indice }}
                          </div>
                          {% if ev.accion == 'CIERRE_EXPEDIENTE' and exp.estado == 'CERRADO' %}
                          <div class="mt-3">
                              <a href="/api/v1/agn/expedientes/{{ exp.id }}/indice_xml" @click.stop class="inline-flex items-center gap-2 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-lg transition-colors shadow-sm w-full justify-center">
                                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14v-8m0 8l-3-3m3 3l3-3"></path></svg>
                                  Descargar XML de Cierre
                              </a>
                          </div>
                          {% endif %}"""

content = content.replace(old_block, new_block)

with open("app/templates/pages/expediente_view.html", "w", encoding="utf-8") as f:
    f.write(content)
