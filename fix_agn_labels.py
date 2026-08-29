with open('app/routers/agn.py', 'r', encoding='utf-8') as f:
    content = f.read()

labels = [
    'Fondo:',
    'Sección:',
    'Subsección (Opcional):',
    'Serie:',
    'Subserie (Opcional):'
]

for label in labels:
    old_html = f'<label class="block text-sm font-semibold text-gray-600 mb-1">{label}</label>'
    new_html = f'''<div class="flex justify-between items-center mb-1">
                    <label class="block text-sm font-semibold text-gray-600">{label}</label>
                    <div class="flex items-center gap-1">
                        <button type="button" class="text-[11px] font-semibold text-primary hover:bg-primary/10 px-1.5 py-0.5 rounded transition-colors">Crear</button>
                        <div class="relative group flex items-center">
                            <span class="flex items-center justify-center w-3.5 h-3.5 rounded-full border border-gray-400 text-gray-400 text-[9px] font-bold cursor-help hover:border-gray-600 hover:text-gray-600 transition-colors">?</span>
                            <div class="absolute bottom-full right-0 mb-1 w-max px-2 py-1 bg-gray-800 text-white text-[10px] font-medium rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all shadow z-[100]">
                                Ayuda próximamente
                                <div class="absolute top-full right-1 border-[3px] border-transparent border-t-gray-800"></div>
                            </div>
                        </div>
                    </div>
                </div>'''
    content = content.replace(old_html, new_html)

# Save the file
with open('app/routers/agn.py', 'w', encoding='utf-8') as f:
    f.write(content)
