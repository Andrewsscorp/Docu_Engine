import re

with open('app/templates/components/explorer_results.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add draggable to the card
card_div = '''<div class="bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow group flex flex-col cursor-pointer relative"'''
new_card_div = '''<div class="bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow group flex flex-col cursor-pointer relative"
                     draggable="true" 
                     @dragstart="event.dataTransfer.setData('text/plain', '{{ doc.id }}'); event.dataTransfer.effectAllowed = 'move';"'''

if card_div in content:
    content = content.replace(card_div, new_card_div)
else:
    # Let's use regex to find the main card div.
    # It has @click="currentDocId = '{{ doc.id }}';
    content = re.sub(
        r'(<div[^>]*@click="currentDocId[^>]*>)',
        r'\1\n                     draggable="true" \n                     @dragstart="event.dataTransfer.setData(\'text/plain\', \'{{ doc.id }}\'); event.dataTransfer.effectAllowed = \'move\';"',
        content
    )

# Add 'Mover' to the 3-dots menu
reassign_button = '''<button @click.stop="menuOpen = false; htmx.ajax('GET', '/api/v1/documentos/{{ doc.id }}/reasignar/ui', {target: 'body', swap: 'beforeend'})" class="w-full text-left px-4 py-2 hover:bg-gray-50 text-gray-700 flex items-center gap-2 font-medium">'''
mover_button = '''<!-- Mover Button -->
                                    <button @click.stop="menuOpen = false; Swal.fire({title: 'Mover Documento', text: 'Arrastra este documento hacia una carpeta en la parte superior.', icon: 'info'});" class="w-full text-left px-4 py-2 hover:bg-gray-50 text-gray-700 flex items-center gap-2 font-medium">
                                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"></path></svg>
                                        Mover
                                    </button>
                                    
                                    <button @click.stop="menuOpen = false; htmx.ajax('GET', '/api/v1/documentos/{{ doc.id }}/reasignar/ui', {target: 'body', swap: 'beforeend'})" class="w-full text-left px-4 py-2 hover:bg-gray-50 text-gray-700 flex items-center gap-2 font-medium">'''

content = content.replace(reassign_button, mover_button)

with open('app/templates/components/explorer_results.html', 'w', encoding='utf-8') as f:
    f.write(content)
