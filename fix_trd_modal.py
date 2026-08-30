with open("app/templates/pages/control_tipologias.html", "r", encoding="utf-8") as f:
    content = f.read()

import re

old_modal = r'<!-- Modal: Vincular Documento -->.*?<div id="modal-trd-container"></div>'

new_modal = """<!-- Modal: Vincular Documento -->
    <div x-show="modalVincular" x-cloak class="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
        <div @click.away="modalVincular = false" class="bg-white rounded-3xl w-full max-w-lg shadow-2xl overflow-hidden animate-fade-in-up">
            <div class="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50">
                <h3 class="font-bold text-slate-800 text-lg">Cargar Documento TRD</h3>
                <button @click="modalVincular = false" class="text-slate-400 hover:text-red-500"><svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg></button>
            </div>
            <div class="p-6">
                <p class="text-sm text-slate-500 mb-4">Sube un archivo directamente desde tu equipo para cumplir con este requerimiento.</p>
                <form id="upload-trd-form" class="space-y-4">
                    <input type="hidden" name="tipologia_id" x-model="tipologiaActiva">
                    
                    <div class="space-y-1">
                        <label class="text-xs font-bold text-slate-400">ARCHIVO PDF</label>
                        <input type="file" name="file" accept=".pdf" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-700 font-medium focus:ring-2 focus:ring-indigo-500 outline-none">
                    </div>
                    
                    <button type="button" @click="submitDirectUpload()" class="w-full mt-4 bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 rounded-xl transition-colors shadow-lg shadow-indigo-200">
                        Cargar y Foliar
                    </button>
                </form>
            </div>
        </div>
    </div>
    <div id="modal-trd-container"></div>
    <script>
    function submitDirectUpload() {
        const form = document.getElementById('upload-trd-form');
        if(!form.checkValidity()) { form.reportValidity(); return; }
        
        const fd = new FormData(form);
        Swal.showLoading();
        fetch('/api/v1/agn/expedientes/{{ exp.id }}/upload_direct', {
            method: 'POST',
            body: fd
        }).then(r => r.json()).then(data => {
            if(data.status === 'success') {
                Swal.fire({icon:'success', title:'Documento Cargado', text:'Se ha vinculado al expediente y al Índice Electrónico.', showConfirmButton:false, timer:2000}).then(() => {
                    htmx.trigger('body', 'reloadControlTipologias');
                });
            } else {
                Swal.fire('Error', 'Fallo en la carga', 'error');
            }
        }).catch(e => Swal.fire('Error', e.message, 'error'));
    }
    </script>
"""

content = re.sub(old_modal, new_modal, content, flags=re.DOTALL)

with open("app/templates/pages/control_tipologias.html", "w", encoding="utf-8") as f:
    f.write(content)
