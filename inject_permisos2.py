import re

with open('app/templates/pages/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

permisos_modal_html = '''
    <!-- Modal de Permisos RBAC -->
    <div x-show="showPermisosModal" x-transition.opacity style="display: none;" class="fixed inset-0 z-[100] flex items-center justify-center p-4 backdrop-blur-sm bg-gray-900/50" 
         @abrirmodalpermisos.window="showPermisosModal = true;"
         @cerrarmodalpermisos.window="showPermisosModal = false;"
         @click.self="showPermisosModal = false">
         
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden animate-fade-in-up">
            <div class="p-6 border-b border-gray-100 flex justify-between items-center bg-slate-50">
                <h3 class="font-bold text-lg text-slate-800">Permisos de Etiqueta</h3>
                <button @click="showPermisosModal = false" class="text-gray-400 hover:text-gray-600">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                </button>
            </div>
            
            <div id="modal-permisos-content">
                <!-- Se inyecta vía HTMX -->
                <div class="flex justify-center py-12">
                    <svg class="animate-spin h-8 w-8 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                </div>
            </div>
        </div>
    </div>
'''

# Find the end of the Edit Modal to append the Permisos Modal after it
marker = "<!-- Modal de Permisos RBAC -->"
if marker not in content:
    # Inject it after the Edit Modal
    if "<!-- El Modal de Edición de Etiquetas -->" in content:
        # Find the end of the Edit Modal
        edit_modal_end = content.find("</form>\n        </div>\n    </div>")
        if edit_modal_end != -1:
            idx = edit_modal_end + len("</form>\n        </div>\n    </div>")
            content = content[:idx] + "\n" + permisos_modal_html + content[idx:]
            with open('app/templates/pages/dashboard.html', 'w', encoding='utf-8') as f:
                f.write(content)
            print("Successfully injected Permisos modal!")
        else:
            print("Could not find end of Edit Modal")
    else:
        print("Could not find Edit Modal")
else:
    print("Permisos modal already exists")
