with open("app/templates/pages/control_tipologias.html", "r", encoding="utf-8") as f:
    content = f.read()

import re

# 1. Update Parametrizar TRD header button container
old_header_btn = """<button hx-get="/api/v1/agn/expedientes/{{ exp.id }}/modal_trd" hx-target="#modal-trd-container" class="px-3 py-1.5 bg-indigo-50 text-indigo-600 hover:bg-indigo-100 font-bold rounded-lg transition-colors flex items-center gap-2 text-sm border border-indigo-200">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                        Parametrizar TRD
                    </button>"""

new_header_btn = """<button hx-get="/api/v1/agn/expedientes/{{ exp.id }}/modal_trd" hx-target="#modal-trd-container" class="px-3 py-1.5 bg-indigo-50 text-indigo-600 hover:bg-indigo-100 font-bold rounded-lg transition-colors flex items-center gap-2 text-sm border border-indigo-200">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                        Parametrizar TRD
                    </button>
                    <button hx-post="/api/v1/agn/expedientes/{{ exp.id }}/importar_trd" hx-target="#expediente-inner-container" class="px-3 py-1.5 bg-emerald-50 text-emerald-600 hover:bg-emerald-100 font-bold rounded-lg transition-colors flex items-center gap-2 text-sm border border-emerald-200" onclick="Swal.showLoading()">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                        Heredar de Subserie
                    </button>"""
content = content.replace(old_header_btn, new_header_btn)

# 2. Update empty state text
old_text = "Esta subserie no tiene tipologías documentales parametrizadas."
new_text = "Este expediente no tiene tipologías documentales parametrizadas."
content = content.replace(old_text, new_text)

# 3. Add Heredar button to the empty state too
old_empty_btn = """<button hx-get="/api/v1/agn/expedientes/{{ exp.id }}/modal_trd" hx-target="#modal-trd-container" class="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl shadow-lg transition-transform hover:scale-105 mx-auto flex items-center gap-2">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>
                            Parametrizar Reglas TRD Ahora
                        </button>"""

new_empty_btn = """<div class="flex items-center justify-center gap-4 mt-6">
                            <button hx-get="/api/v1/agn/expedientes/{{ exp.id }}/modal_trd" hx-target="#modal-trd-container" class="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl shadow-lg transition-transform hover:scale-105 flex items-center gap-2">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>
                                Parametrizar Reglas
                            </button>
                            <button hx-post="/api/v1/agn/expedientes/{{ exp.id }}/importar_trd" hx-target="#expediente-inner-container" class="px-6 py-3 bg-white border border-slate-200 hover:border-emerald-500 hover:text-emerald-600 text-slate-700 font-bold rounded-xl shadow-sm transition-colors flex items-center gap-2" onclick="Swal.showLoading()">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                                Heredar de Subserie
                            </button>
                        </div>"""
content = content.replace(old_empty_btn, new_empty_btn)

with open("app/templates/pages/control_tipologias.html", "w", encoding="utf-8") as f:
    f.write(content)
