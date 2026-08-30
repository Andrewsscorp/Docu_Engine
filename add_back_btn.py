with open("app/templates/pages/control_tipologias.html", "r", encoding="utf-8") as f:
    content = f.read()

old_header = """<!-- Header -->
    <div class="bg-white px-8 py-6 border-b border-gray-200">"""
    
new_header = """<!-- Header -->
    <div class="bg-white px-8 py-6 border-b border-gray-200">
        <button hx-get="/api/v1/agn/expedientes/{{ exp.id }}/view" hx-target="#expediente-inner-container" class="mb-4 text-indigo-600 font-bold hover:underline flex items-center gap-1 w-max text-sm">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
            Volver a los Documentos del Expediente
        </button>"""
        
content = content.replace(old_header, new_header)

with open("app/templates/pages/control_tipologias.html", "w", encoding="utf-8") as f:
    f.write(content)
