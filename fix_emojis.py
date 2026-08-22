with open('app/routers/etiquetas.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace corrupted emojis
content = content.replace('<span class="mr-2">Y\"\'</span> Editar', '<span class="mr-2">✏️</span> Editar')
content = content.replace('<span class="mr-2">o??</span> Editar', '<span class="mr-2">✏️</span> Editar')
content = content.replace('<span class="mr-2">Y-\'?</span> Desactivar', '<span class="mr-2">🗑️</span> Desactivar')
content = content.replace('<span class="mr-2">Y-\'?</span> Sistema', '<span class="mr-2">🗑️</span> Sistema')

with open('app/routers/etiquetas.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed emojis!")
