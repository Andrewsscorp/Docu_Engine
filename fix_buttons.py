with open("app/templates/pages/control_tipologias.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add "Limpiar TRD" button next to "Heredar de Subserie"
limpiar_btn = """<button hx-delete="/api/v1/agn/expedientes/{{ exp.id }}/tipologias" 
                            hx-target="#expediente-inner-container" 
                            hx-confirm="¿Estás seguro de eliminar todos los requerimientos? Los documentos ya subidos no se borrarán."
                            class="px-3 py-1.5 bg-red-50 text-red-600 hover:bg-red-100 font-bold rounded-lg transition-colors flex items-center gap-2 text-sm border border-red-200">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                        Limpiar TRD
                    </button>"""

content = content.replace(
    'Heredar de Subserie\n                    </button>',
    'Heredar de Subserie\n                    </button>\n                    ' + limpiar_btn
)

# 2. Add individual Delete button to CARGADO state
old_cargado_end = """        </div>
                    </div>"""
new_cargado_end = """        </div>
                        <button hx-delete="/api/v1/agn/expedientes/{{ exp.id }}/tipologias/{{ req.tipologia_id }}"
                                hx-target="#expediente-inner-container"
                                hx-confirm="¿Desvincular este requisito del expediente?"
                                class="p-2 text-slate-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors" title="Eliminar requisito">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                        </button>
                    </div>"""
# Apply only once for the obligatorias section
if old_cargado_end in content:
    content = content.replace(old_cargado_end, new_cargado_end, 1)

# 3. Add individual Delete button to pending state
old_pending_btn = """<button @click="abrirModal('{{ req.tipologia_id }}')" class="px-4 py-2 bg-slate-900 text-white rounded-lg font-bold text-sm hover:bg-slate-800 transition-colors flex items-center gap-2 shadow-md">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path></svg>
                            Cargar Documento
                        </button>"""
new_pending_btn = """<div class="flex items-center gap-2">
                            <button @click="abrirModal('{{ req.tipologia_id }}')" class="px-4 py-2 bg-slate-900 text-white rounded-lg font-bold text-sm hover:bg-slate-800 transition-colors flex items-center gap-2 shadow-md">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path></svg>
                                Cargar Documento
                            </button>
                            <button hx-delete="/api/v1/agn/expedientes/{{ exp.id }}/tipologias/{{ req.tipologia_id }}"
                                    hx-target="#expediente-inner-container"
                                    class="p-2 text-red-300 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors border border-transparent hover:border-red-100" title="Eliminar requisito">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                            </button>
                        </div>"""
if old_pending_btn in content:
    content = content.replace(old_pending_btn, new_pending_btn)


with open("app/templates/pages/control_tipologias.html", "w", encoding="utf-8") as f:
    f.write(content)
