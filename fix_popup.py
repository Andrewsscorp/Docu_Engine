import re

with open('app/templates/components/explorer.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace createFolder() Javascript
old_js = '''        function createFolder() {
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
        }'''

new_js = '''        // Variable global para almacenar el color seleccionado en el popup
        let selectedFolderColor = '#4648d4'; // Azul por defecto

        function selectColor(colorHex, element) {
            selectedFolderColor = colorHex;
            // Remover estilos de seleccionado de todos los circulos
            document.querySelectorAll('.color-circle').forEach(el => {
                el.classList.remove('ring-4', 'ring-offset-2', 'ring-gray-200');
                el.innerHTML = '';
            });
            // Agregar estilo de seleccionado al circulo actual
            element.classList.add('ring-4', 'ring-offset-2', 'ring-gray-200');
            element.innerHTML = '<svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path></svg>';
        }

        function createFolder() {
            selectedFolderColor = '#4648d4'; // Reset default blue
            
            Swal.fire({
                showCloseButton: true,
                showConfirmButton: false,
                customClass: {
                    popup: 'rounded-2xl',
                    htmlContainer: 'text-left m-0 p-0'
                },
                html: 
                    <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center">
                        <h2 class="text-xl font-bold text-gray-800 font-sans">Nueva Carpeta</h2>
                    </div>
                    <div class="p-6">
                        <div class="mb-5">
                            <label class="block text-sm font-semibold text-gray-600 mb-2">Nombre de la carpeta</label>
                            <input id="swal-input-name" type="text" class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none text-gray-700" placeholder="Ej. Facturas Q3">
                        </div>
                        
                        <div class="mb-2">
                            <label class="block text-sm font-semibold text-gray-600 mb-3">Color de etiqueta</label>
                            <div class="flex items-center gap-3">
                                <!-- Red -->
                                <button type="button" onclick="selectColor('#f87171', this)" class="color-circle w-9 h-9 rounded-full bg-red-400 hover:scale-110 transition-transform flex items-center justify-center"></button>
                                <!-- Green -->
                                <button type="button" onclick="selectColor('#4ade80', this)" class="color-circle w-9 h-9 rounded-full bg-green-400 hover:scale-110 transition-transform flex items-center justify-center"></button>
                                <!-- Blue (Default Selected) -->
                                <button type="button" onclick="selectColor('#4648d4', this)" class="color-circle w-9 h-9 rounded-full bg-primary ring-4 ring-offset-2 ring-gray-200 hover:scale-110 transition-transform flex items-center justify-center">
                                    <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path></svg>
                                </button>
                                <!-- Yellow -->
                                <button type="button" onclick="selectColor('#fbbf24', this)" class="color-circle w-9 h-9 rounded-full bg-yellow-400 hover:scale-110 transition-transform flex items-center justify-center"></button>
                                <!-- Purple -->
                                <button type="button" onclick="selectColor('#c084fc', this)" class="color-circle w-9 h-9 rounded-full bg-purple-400 hover:scale-110 transition-transform flex items-center justify-center"></button>
                                <!-- Gray -->
                                <button type="button" onclick="selectColor('#9ca3af', this)" class="color-circle w-9 h-9 rounded-full bg-gray-400 hover:scale-110 transition-transform flex items-center justify-center"></button>
                            </div>
                        </div>
                    </div>
                    <div class="bg-gray-50 px-6 py-4 rounded-b-2xl flex justify-end gap-3">
                        <button type="button" onclick="Swal.close()" class="px-5 py-2.5 text-sm font-medium text-gray-600 hover:bg-gray-200 rounded-xl transition-colors">Cancelar</button>
                        <button type="button" onclick="submitCreateFolder()" class="px-6 py-2.5 text-sm font-bold text-white bg-primary hover:bg-primary/90 rounded-xl shadow-sm transition-colors">Crear</button>
                    </div>
                
            });
        }
        
        function submitCreateFolder() {
            const nameInput = document.getElementById('swal-input-name');
            if(!nameInput.value.trim()) {
                nameInput.focus();
                nameInput.classList.add('border-red-500');
                return;
            }
            
            let formData = new FormData();
            formData.append('name', nameInput.value.trim());
            formData.append('color', selectedFolderColor);
            
            Swal.showLoading();
            
            fetch('/api/v1/folders', {
                method: 'POST',
                body: formData
            }).then(res => res.json()).then(data => {
                if(data.status === 'success') {
                    htmx.trigger('body', 'reloadExplorer');
                    Swal.fire({toast: true, position: 'top-end', icon: 'success', title: 'Carpeta creada', showConfirmButton: false, timer: 2000});
                } else {
                    Swal.fire('Error', data.message || 'No se pudo crear la carpeta', 'error');
                }
            }).catch(err => {
                Swal.fire('Error', 'Hubo un problema de conexión', 'error');
            });
        }'''

if old_js in content:
    content = content.replace(old_js, new_js)
else:
    # Use regex to find createFolder if it slightly differs
    content = re.sub(r'function createFolder\(\) \{.*?\n        \}(?=\s*function moveDoc)', new_js, content, flags=re.DOTALL)

with open('app/templates/components/explorer.html', 'w', encoding='utf-8') as f:
    f.write(content)
