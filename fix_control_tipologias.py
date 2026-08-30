with open("app/templates/pages/control_tipologias.html", "r", encoding="utf-8") as f:
    content = f.read()

import re

# We want to conditionally show the matrix or an empty state with a "Configurar Matriz TRD" button
# Wait, I can just put a button in the Header to always allow configuration for Admins!
new_header = """<!-- Header -->
    <div class="bg-white px-8 py-6 border-b border-gray-200">
        <button hx-get="/api/v1/agn/expedientes/{{ exp.id }}/view" hx-target="#expediente-inner-container" class="mb-4 text-indigo-600 font-bold hover:underline flex items-center gap-1 w-max text-sm">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
            Volver a los Documentos del Expediente
        </button>
        <div class="flex justify-between items-start">
            <div>
                <p class="text-sm font-bold text-gray-400 flex items-center gap-2 mb-1">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"></path></svg>
                    Expediente: {{ exp.codigo_expediente }}
                </p>
                <div class="flex items-center gap-4">
                    <h2 class="text-2xl font-extrabold text-slate-800 tracking-tight">Control de Tipologías Documentales</h2>
                    <button hx-get="/api/v1/agn/subseries/{{ exp.subserie_id }}/modal_trd" hx-target="#modal-trd-container" class="px-3 py-1.5 bg-indigo-50 text-indigo-600 hover:bg-indigo-100 font-bold rounded-lg transition-colors flex items-center gap-2 text-sm border border-indigo-200">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                        Parametrizar TRD
                    </button>
                </div>
            </div>"""

old_header = """<!-- Header -->
    <div class="bg-white px-8 py-6 border-b border-gray-200">
        <button hx-get="/api/v1/agn/expedientes/{{ exp.id }}/view" hx-target="#expediente-inner-container" class="mb-4 text-indigo-600 font-bold hover:underline flex items-center gap-1 w-max text-sm">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
            Volver a los Documentos del Expediente
        </button>
        <div class="flex justify-between items-start">
            <div>
                <p class="text-sm font-bold text-gray-400 flex items-center gap-2 mb-1">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"></path></svg>
                    Expediente: {{ exp.codigo_expediente }}
                </p>
                <h2 class="text-2xl font-extrabold text-slate-800 tracking-tight">Control de Tipologías Documentales</h2>
            </div>"""

content = content.replace(old_header, new_header)

empty_state = """
            <!-- Left Column: Mandatory -->
            <div class="flex-1 space-y-4">
                <h3 class="text-lg font-bold text-slate-800 flex items-center gap-2 mb-4">
                    <svg class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                    Documentos Obligatorios (TRD)
                </h3>
                
                {% if obligatorias|length == 0 and opcionales|length == 0 %}
                <div class="bg-indigo-50 border-2 border-dashed border-indigo-200 rounded-2xl p-12 text-center">
                    <svg class="w-16 h-16 text-indigo-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                    <h4 class="text-xl font-bold text-indigo-900 mb-2">Matriz TRD Vacía</h4>
                    <p class="text-indigo-600 mb-6">Esta subserie no tiene tipologías documentales parametrizadas. El expediente no puede validarse ni sellarse hasta que un administrador configure las reglas de negocio.</p>
                    <button hx-get="/api/v1/agn/subseries/{{ exp.subserie_id }}/modal_trd" hx-target="#modal-trd-container" class="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl shadow-lg transition-transform hover:scale-105 mx-auto flex items-center gap-2">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>
                        Parametrizar Reglas TRD Ahora
                    </button>
                </div>
                {% endif %}
                
                {% for req in obligatorias %}"""

old_empty = """
            <!-- Left Column: Mandatory -->
            <div class="flex-1 space-y-4">
                <h3 class="text-lg font-bold text-slate-800 flex items-center gap-2 mb-4">
                    <svg class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                    Documentos Obligatorios (TRD)
                </h3>
                
                {% for req in obligatorias %}"""

content = content.replace(old_empty, empty_state)

# I also need a div for the modal
end_div = "</div>\n    <div id=\"modal-trd-container\"></div>\n</div>"
content = content.replace("</div>\n</div>", end_div)

with open("app/templates/pages/control_tipologias.html", "w", encoding="utf-8") as f:
    f.write(content)
