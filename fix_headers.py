with open("app/templates/pages/expediente_view.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if i == 186:
        # metadataModal header
        new_lines.append('            <div class="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50">\n')
        new_lines.append('                <h3 class="font-bold text-slate-800 text-xl flex items-center gap-2">\n')
        new_lines.append('                    <svg class="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>\n')
        new_lines.append('                    Metadatos del Expediente\n')
        new_lines.append('                </h3>\n')
        new_lines.append('                <button @click="metadataModal = false" class="text-slate-400 hover:text-red-500"><svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg></button>\n')
        new_lines.append('            </div>\n')
        skip = True
    elif i == 186 + 14:
        skip = False
    elif i == 245:
        # addDocModal header
        new_lines.append('            <div class="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50">\n')
        new_lines.append('                <h3 class="font-bold text-slate-800 text-xl">Nuevo Documento</h3>\n')
        new_lines.append('                <button @click="addDocModal = false" class="text-slate-400 hover:text-red-500"><svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg></button>\n')
        new_lines.append('            </div>\n')
        skip = True
    elif i == 245 + 14:
        skip = False
        
    if not skip:
        new_lines.append(line)

with open("app/templates/pages/expediente_view.html", "w", encoding="utf-8") as f:
    f.writelines(new_lines)
