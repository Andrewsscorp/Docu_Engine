import re

with open('app/templates/components/explorer_results.html', 'r', encoding='utf-8') as f:
    content = f.read()

bad_mover = '''<button @click.stop="menuOpen = false; Swal.fire({title: 'Mover Documento', text: 'Arrastra este documento hacia una carpeta en la parte superior.', icon: 'info'});" class="w-full text-left px-4 py-2 hover:bg-gray-50 text-gray-700 flex items-center gap-2 font-medium">'''

good_mover = '''<button @click.stop="menuOpen = false; openMoveModal('{{ doc.id }}');" class="w-full text-left px-4 py-2 hover:bg-gray-50 text-gray-700 flex items-center gap-2 font-medium">'''

content = content.replace(bad_mover, good_mover)

with open('app/templates/components/explorer_results.html', 'w', encoding='utf-8') as f:
    f.write(content)
