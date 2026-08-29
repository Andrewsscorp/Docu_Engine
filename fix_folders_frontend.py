import re

with open('app/templates/components/explorer.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Update x-data
content = content.replace(
    '''x-data="{ vista: 'cuadricula', drawerAbierto: false, currentDocId: null }"''',
    '''x-data="{ vista: 'cuadricula', drawerAbierto: false, currentDocId: null, typeFilter: '', dateFilter: '', statusFilter: '' }"'''
)

# Update hx-include in the search bar
content = content.replace(
    '''hx-include="[name='sort'], [name='view'], [name='group_id'], [name='status']"''',
    '''hx-include="[name='sort'], [name='view'], [name='group_id'], [name='status'], [name='type_filter'], [name='date_filter']"'''
)

folders_and_filters = '''    <!-- Hidden inputs for filters -->
    <input type="hidden" name="type_filter" x-model="typeFilter">
    <input type="hidden" name="date_filter" x-model="dateFilter">
    <input type="hidden" name="status" x-model="statusFilter">

    <!-- Quick Filters -->
    <section class="bg-white p-4 rounded-2xl border border-gray-200 shadow-sm flex flex-wrap items-center gap-4 mb-6">
      <div class="flex flex-wrap gap-2 border-r border-gray-200 pr-4">
        <button @click="typeFilter = ''; htmx.trigger('input[name=q]', 'search')" :class="typeFilter === '' ? 'bg-primary text-white shadow-sm' : 'text-gray-600 hover:bg-gray-50'" class="px-4 py-2 rounded-lg font-medium text-sm transition-colors">Todos</button>
        <button @click="typeFilter = 'pdf'; htmx.trigger('input[name=q]', 'search')" :class="typeFilter === 'pdf' ? 'bg-primary text-white shadow-sm' : 'text-gray-600 hover:bg-gray-50'" class="px-4 py-2 rounded-lg font-medium text-sm transition-colors">PDFs</button>
        <button @click="typeFilter = 'images'; htmx.trigger('input[name=q]', 'search')" :class="typeFilter === 'images' ? 'bg-primary text-white shadow-sm' : 'text-gray-600 hover:bg-gray-50'" class="px-4 py-2 rounded-lg font-medium text-sm transition-colors">Imágenes</button>
      </div>
      <div class="flex flex-1 flex-wrap gap-3 items-center">
        <div class="relative">
          <select x-model="dateFilter" @change="htmx.trigger('input[name=q]', 'search')" class="appearance-none bg-gray-50 border border-gray-200 rounded-lg py-2 pl-3 pr-10 text-sm text-gray-700 focus:outline-none focus:border-primary">
            <option value="">Cualquier fecha</option>
            <option value="week">Última semana</option>
            <option value="month">Este mes</option>
            <option value="year">Este año</option>
          </select>
          <svg class="w-4 h-4 absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
        </div>
        <div class="relative">
          <select x-model="statusFilter" @change="htmx.trigger('input[name=q]', 'search')" class="appearance-none bg-gray-50 border border-gray-200 rounded-lg py-2 pl-3 pr-10 text-sm text-gray-700 focus:outline-none focus:border-primary">
            <option value="">Todos los estados</option>
            <option value="COMPLETED">Listo</option>
            <option value="PENDING">Pendiente</option>
          </select>
          <svg class="w-4 h-4 absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"></path></svg>
        </div>
        
        <!-- Create Folder Button (Red) -->
        <button @click="createFolder()" class="ml-auto flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white font-medium text-sm py-2 px-4 rounded-lg transition-colors shadow-sm">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
          Nueva Carpeta
        </button>
      </div>
    </section>
    
    <!-- Folders Section -->
    <section class="mb-8" x-data="{ dragHover: null }">
        <div class="flex justify-between items-end mb-4">
            <h3 class="text-xl text-gray-800 font-bold">Carpetas</h3>
            <button class="text-primary font-medium hover:underline text-sm">Ver todo</button>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            {% for folder in folders %}
            <div class="bg-white rounded-2xl p-5 border border-gray-200 shadow-sm hover:shadow-md transition-all cursor-pointer flex items-center gap-4 group"
                 :class="dragHover === '{{ folder.id }}' ? 'border-primary ring-2 ring-primary/20 bg-primary/5 scale-105' : ''"
                 @click="htmx.ajax('GET', '/api/v1/documents/explorer?folder_filter={{ folder.id }}', {target: '#explorer-results'})"
                 @dragover.prevent="dragHover = '{{ folder.id }}'"
                 @dragleave.prevent="dragHover = null"
                 @drop.prevent="dragHover = null; moveDoc(event.dataTransfer.getData('text/plain'), '{{ folder.id }}')">
                <div class="w-12 h-12 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform" style="background-color: {{ folder.color }}20; color: {{ folder.color }};">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"></path></svg>
                </div>
                <div>
                    <h4 class="font-bold text-gray-800">{{ folder.name }}</h4>
                    <p class="text-xs text-gray-500 mt-0.5">{{ folder.doc_count }} Archivos</p>
                </div>
            </div>
            {% endfor %}
            {% if not folders %}
            <div class="col-span-full py-8 text-center text-gray-400 text-sm border-2 border-dashed border-gray-200 rounded-2xl">
                Aún no tienes carpetas. Haz clic en "Nueva Carpeta" para crear una.
            </div>
            {% endif %}
        </div>
    </section>

    <!-- JS Helper Functions -->
    <script>
        function createFolder() {
            Swal.fire({
                title: 'Nueva Carpeta',
                html: 
                    <input id="swal-input1" class="swal2-input" placeholder="Nombre de la carpeta">
                    <div class="mt-4 flex items-center justify-center gap-2">
                        <label>Color:</label>
                        <input id="swal-input2" type="color" value="#4648d4" class="w-10 h-10 p-0 border-0 cursor-pointer">
                    </div>
                ,
                focusConfirm: false,
                showCancelButton: true,
                confirmButtonText: 'Crear',
                cancelButtonText: 'Cancelar',
                preConfirm: () => {
                    return [
                        document.getElementById('swal-input1').value,
                        document.getElementById('swal-input2').value
                    ]
                }
            }).then((result) => {
                if (result.isConfirmed && result.value[0]) {
                    let formData = new FormData();
                    formData.append('name', result.value[0]);
                    formData.append('color', result.value[1]);
                    
                    fetch('/api/v1/folders', {
                        method: 'POST',
                        body: formData
                    }).then(res => res.json()).then(data => {
                        if(data.status === 'success') {
                            htmx.trigger('body', 'reloadExplorer');
                            Swal.fire({toast: true, position: 'top-end', icon: 'success', title: 'Carpeta creada', showConfirmButton: false, timer: 2000});
                        }
                    });
                }
            });
        }
        
        function moveDoc(docId, folderId) {
            if(!docId) return;
            let formData = new FormData();
            formData.append('folder_id', folderId);
            
            fetch('/api/v1/documentos/' + docId + '/mover', {
                method: 'POST',
                body: formData
            }).then(res => {
                if(res.ok) {
                    htmx.trigger('body', 'reloadExplorer');
                    Swal.fire({toast: true, position: 'top-end', icon: 'success', title: 'Documento movido a carpeta', showConfirmButton: false, timer: 2000});
                }
            });
        }
    </script>
'''

content = content.replace('    <!-- Header Controls -->', folders_and_filters + '\n    <!-- Header Controls -->')

with open('app/templates/components/explorer.html', 'w', encoding='utf-8') as f:
    f.write(content)
