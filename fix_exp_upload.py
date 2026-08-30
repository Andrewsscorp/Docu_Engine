with open("app/templates/pages/expediente_view.html", "r", encoding="utf-8") as f:
    content = f.read()

import re

old_modal = r'<!-- Modal: Vincular Documento -->.*?function showTxInfo'

new_modal = """<!-- Modal: Vincular Documento -->
    <div x-show="addDocModal" x-cloak class="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
        <div @click.away="addDocModal = false" class="bg-white rounded-3xl w-full max-w-xl shadow-2xl overflow-hidden animate-fade-in-up">
            <div class="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50">
                <h3 class="font-bold text-slate-800 text-xl">Nuevo Documento</h3>
                <button @click="addDocModal = false" class="text-slate-400 hover:text-red-500"><svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg></button>
            </div>
            <form id="vincular-form" class="p-6 space-y-5">
                <div>
                    <label class="block text-sm font-bold text-slate-700 mb-2">Subir Archivo PDF:*</label>
                    <input type="file" name="file" accept=".pdf" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm">
                </div>
                <div>
                    <label class="block text-sm font-bold text-slate-700 mb-2">Clasificar Tipología Documental:*</label>
                    <select name="tipologia_id" required x-model="selectedTipo" class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm">
                        <option value="">-- Seleccionar Tipo --</option>
                        {% for tip in tipologias %}
                        <option value="{{ tip.id }}">{{ tip.nombre_oficial }} {% if tip.obligatoria %}(Requerido){% endif %}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="pt-4 border-t border-slate-100 flex justify-end gap-3">
                    <button type="button" @click="addDocModal = false" class="px-6 py-2.5 rounded-xl font-bold text-slate-600 bg-slate-100 hover:bg-slate-200 transition-colors">Cancelar</button>
                    <button type="button" @click="submitVincular()" :disabled="!selectedTipo" class="px-6 py-2.5 rounded-xl font-bold text-white bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 transition-colors shadow-md">
                        Cargar al Expediente
                    </button>
                </div>
            </form>
        </div>
    </div>
    <script>
        function submitVincular() {
            const form = document.getElementById('vincular-form');
            if (!form.checkValidity()) { form.reportValidity(); return; }
            
            const formData = new FormData(form);
            Swal.showLoading();
            fetch('/api/v1/agn/expedientes/{{ exp.id }}/upload_direct', {
                method: 'POST',
                body: formData
            }).then(r => r.json()).then(data => {
                if(data.status === 'success') {
                    Swal.fire({icon: 'success', title: 'Documento Cargado', html: 'Índice Electrónico actualizado exitosamente.', showConfirmButton: false, timer: 2000}).then(() => {
                        htmx.ajax('GET', '/api/v1/agn/expedientes/{{ exp.id }}/view', {target: '#expediente-inner-container'});
                    });
                } else {
                    Swal.fire('Error', data.detail || 'Error al vincular', 'error');
                }
            }).catch(e => Swal.fire('Error', e.message, 'error'));
        }

        function showTxInfo"""

content = re.sub(old_modal, new_modal, content, flags=re.DOTALL)

with open("app/templates/pages/expediente_view.html", "w", encoding="utf-8") as f:
    f.write(content)
