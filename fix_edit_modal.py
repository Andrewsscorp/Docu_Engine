import re

with open('app/templates/pages/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

edit_modal_html = '''
    <!-- El Modal de Edición de Etiquetas -->
    <div x-show="showEditModal" x-transition.opacity style="display: none;" class="fixed inset-0 z-[100] flex items-center justify-center p-4 backdrop-blur-sm bg-gray-900/50" 
         @edit-tag.window="
            showEditModal = true; 
            editTagId = .detail.id; 
            tagName = .detail.nombre; 
            currentBg = .detail.bg; 
            currentText = .detail.text; 
            tagCat = .detail.cat;
            selectedTheme = themes.find(t => t.bg === currentBg)?.id || 'indigo';
         "
         @click.self="showEditModal = false">
         
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden animate-fade-in-up" x-data="{ 
            editTagId: '',
            tagName: '',
            currentBg: 'bg-indigo-100',
            currentText: 'text-indigo-700',
            tagCat: 'Estado',
            selectedTheme: 'indigo',
            themes: [
                { id: 'indigo', bg: 'bg-indigo-100', text: 'text-indigo-700', label: 'Índigo' },
                { id: 'emerald', bg: 'bg-emerald-100', text: 'text-emerald-700', label: 'Esmeralda' },
                { id: 'rose', bg: 'bg-rose-100', text: 'text-rose-700', label: 'Rosa' },
                { id: 'amber', bg: 'bg-amber-100', text: 'text-amber-700', label: 'Ámbar' },
                { id: 'purple', bg: 'bg-purple-100', text: 'text-purple-700', label: 'Púrpura' },
                { id: 'slate', bg: 'bg-slate-100', text: 'text-slate-700', label: 'Pizarra' }
            ]
        }" @change-theme="currentBg = $event.detail.bg; currentText = $event.detail.text">
            
            <div class="p-6 border-b border-gray-100 flex justify-between items-center bg-slate-50">
                <h3 class="font-bold text-lg text-slate-800">Editar Etiqueta</h3>
                <button @click="showEditModal = false" class="text-gray-400 hover:text-gray-600">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                </button>
            </div>
            
            <form @submit.prevent="
                const fd = new FormData();
                fd.append('nombre', tagName);
                fd.append('color_fondo', currentBg);
                fd.append('color_texto', currentText);
                fd.append('categoria', tagCat);
                fetch('/api/v1/etiquetas/' + editTagId, {
                    method: 'PUT',
                    body: fd,
                    headers: {'HX-Request': 'true'}
                }).then(res => {
                    const triggerHeader = res.headers.get('hx-trigger');
                    if (triggerHeader && triggerHeader.includes('alertaForense')) {
                        const data = JSON.parse(triggerHeader);
                        window.dispatchEvent(new CustomEvent('alertaforense', {detail: data.alertaForense}));
                    } else if (res.ok) {
                        res.text().then(html => {
                            if(html) {
                                document.getElementById('etiqueta-row-' + editTagId).outerHTML = html;
                            }
                            showEditModal = false;
                            window.dispatchEvent(new CustomEvent('toastexito', {detail: {mensaje: 'Etiqueta editada con éxito'}}));
                        });
                    } else {
                        Swal.fire('Error', 'No se pudo editar', 'error');
                    }
                })
            " class="p-6">
                
                <div class="mb-6 flex justify-center py-4 bg-gray-50/50 rounded-xl border border-gray-100 border-dashed">
                    <span class="px-3 py-1 text-xs font-semibold rounded-full transition-colors" 
                          :class="currentBg + ' ' + currentText" 
                          x-text="tagName || 'Vista Previa'"></span>
                </div>
                
                <div class="mb-5">
                    <label class="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
                    <input type="text" name="nombre" x-model="tagName" maxlength="20" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500">
                </div>
                
                <div class="mb-5">
                    <label class="block text-sm font-medium text-gray-700 mb-1">Categoría</label>
                    <select name="categoria" x-model="tagCat" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500">
                        <option value="Estado">Estado (Workflow)</option>
                        <option value="Clasificación">Clasificación (Metadato)</option>
                        <option value="Prioridad">Prioridad</option>
                    </select>
                </div>
                
                <div class="mb-6">
                    <label class="block text-sm font-medium text-gray-700 mb-3">Color del Tema</label>
                    <div class="grid grid-cols-6 gap-2">
                        <template x-for="theme in themes" :key="theme.id">
                            <button type="button" @click="selectedTheme = theme.id; ('change-theme', theme)" 
                                    class="w-10 h-10 rounded-full flex items-center justify-center transition-transform hover:scale-110 focus:outline-none"
                                    :class="theme.bg + ' ' + theme.text + (selectedTheme === theme.id ? ' ring-2 ring-offset-2 ring-indigo-500' : '')"
                                    :title="theme.label">
                                <svg x-show="selectedTheme === theme.id" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                            </button>
                        </template>
                    </div>
                </div>
                
                <div class="flex justify-end gap-3 mt-8">
                    <button type="button" @click="showEditModal = false" class="px-4 py-2 text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg font-medium transition-colors">Cancelar</button>
                    <button type="submit" :disabled="!tagName || !selectedTheme" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed">Actualizar Etiqueta</button>
                </div>
            </form>
        </div>
    </div>
'''

if "El Modal de Edición de Etiquetas" not in content:
    # Replace the last occurrence of <!-- Modal de Permisos RBAC --> with the Edit Modal BEFORE it.
    # Wait, the easiest way is to inject it right before <!-- END TAGS VIEW -->.
    # But it must be inside the <section>
    
    # We can inject it right before <!-- Modal de Permisos RBAC -->
    if "<!-- Modal de Permisos RBAC -->" in content:
        content = content.replace("<!-- Modal de Permisos RBAC -->", edit_modal_html + "\n\n<!-- Modal de Permisos RBAC -->")
    else:
        # Fallback
        content = content.replace("</section>\n<!-- END TAGS VIEW -->", edit_modal_html + "\n</section>\n<!-- END TAGS VIEW -->")

    with open('app/templates/pages/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Injected Edit Modal successfully")
else:
    print("Edit modal already exists?!")
