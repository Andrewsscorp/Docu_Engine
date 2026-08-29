import re

with open('app/templates/components/explorer.html', 'r', encoding='utf-8') as f:
    content = f.read()

folders_script = '''    <!-- JS Helper Functions -->
    <script>
        const availableFolders = [
            {% for folder in folders %}
            { id: '{{ folder.id }}', name: '{{ folder.name }}', color: '{{ folder.color }}' },
            {% endfor %}
        ];
        
        function openMoveModal(docId) {
            if (availableFolders.length === 0) {
                Swal.fire('Sin carpetas', 'Crea primero una carpeta para poder mover documentos.', 'info');
                return;
            }
            
            let optionsHtml = '<div class="flex flex-col gap-2 mt-4 text-left">';
            availableFolders.forEach(f => {
                optionsHtml += 
                    <button onclick="Swal.close(); moveDoc('', '')" class="w-full px-4 py-3 border border-gray-200 rounded-xl hover:bg-gray-50 flex items-center gap-3 transition-colors text-left">
                        <div class="w-8 h-8 rounded-lg flex items-center justify-center" style="background-color: 20; color: ;">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"></path></svg>
                        </div>
                        <span class="font-bold text-gray-700 font-sans"></span>
                    </button>
                ;
            });
            optionsHtml += '</div>';
            
            Swal.fire({
                title: 'Mover a carpeta',
                html: optionsHtml,
                showConfirmButton: false,
                showCloseButton: true,
                customClass: {
                    popup: 'rounded-2xl font-sans'
                }
            });
        }
'''

content = content.replace('    <!-- JS Helper Functions -->\n    <script>', folders_script)

with open('app/templates/components/explorer.html', 'w', encoding='utf-8') as f:
    f.write(content)
