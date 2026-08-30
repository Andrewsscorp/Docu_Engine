with open("app/templates/pages/expediente_view.html", "r", encoding="utf-8") as f:
    content = f.read()

# Fix 1: Auto-adjust header and add Metadata button
old_header = """<h2 class="text-3xl font-extrabold text-slate-800 tracking-tight">Expediente: {{ exp.codigo_expediente }}</h2>"""
new_header = """<div class="flex items-center gap-3">
                    <h2 class="text-2xl lg:text-3xl font-extrabold text-slate-800 tracking-tight break-all">{{ exp.codigo_expediente }}</h2>
                    <button @click="metadataModal = true" class="shrink-0 p-2 text-indigo-600 bg-indigo-50 hover:bg-indigo-100 rounded-xl transition-colors tooltip" title="Ver Metadatos TRD">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    </button>
                </div>"""
content = content.replace(old_header, new_header)

# Fix x-data to include modals
content = content.replace('x-data="{ addDocModal: false, selectedDoc: \'\', selectedTipo: \'\' }"', 'x-data="{ addDocModal: false, metadataModal: false, selectedDoc: \'\', selectedTipo: \'\' }"')

# Fix 2: Timeline clickable events
import re
old_timeline_item = """<div class="relative pl-6">
                        <div class="absolute -left-1.5 top-1.5 w-3 h-3 bg-indigo-500 rounded-full ring-4 ring-indigo-50"></div>
                        <div class="text-xs text-indigo-600 font-bold mb-1">{{ ev.fecha_str }}</div>
                        <div class="font-bold text-slate-800 mb-0.5">{{ ev.accion_str }}</div>
                        <div class="text-xs text-slate-500 mb-2">Usuario: {{ ev.usuario_id }}</div>
                        <div class="bg-slate-50 p-2 rounded-lg border border-slate-200 font-mono text-[10px] text-slate-400 break-all">
                            Tx: {{ ev.firma_indice }}
                        </div>
                    </div>"""
new_timeline_item = """<div class="relative pl-6 p-2 -ml-2 rounded-xl hover:bg-indigo-50/50 cursor-pointer transition-colors group" @click="showTxInfo('{{ ev.firma_indice }}', '{{ ev.accion_str }}', '{{ ev.fecha_str }}', '{{ ev.usuario_id }}', '{{ ev.documento_id or 'Ninguno' }}')">
                        <div class="absolute left-0.5 top-3.5 w-3 h-3 bg-indigo-500 rounded-full ring-4 ring-white group-hover:ring-indigo-50 transition-all"></div>
                        <div class="text-xs text-indigo-600 font-bold mb-1">{{ ev.fecha_str }}</div>
                        <div class="font-bold text-slate-800 mb-0.5 group-hover:text-indigo-700 transition-colors">{{ ev.accion_str }}</div>
                        <div class="text-xs text-slate-500 mb-2">Usuario: {{ ev.usuario_id }}</div>
                        <div class="bg-slate-50 group-hover:bg-white p-2 rounded-lg border border-slate-200 font-mono text-[10px] text-slate-400 break-all transition-colors">
                            Tx: {{ ev.firma_indice }}
                        </div>
                    </div>"""
content = content.replace(old_timeline_item, new_timeline_item)

# Fix 3: Add Metadata Modal & SweetAlert JS
new_modals = """
    <!-- Modal: Metadatos -->
    <div x-show="metadataModal" x-cloak class="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
        <div @click.away="metadataModal = false" class="bg-white rounded-3xl w-full max-w-2xl shadow-2xl overflow-hidden animate-fade-in-up">
            <div class="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50">
                <h3 class="font-bold text-slate-800 text-xl flex items-center gap-2">
                    <svg class="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                    Metadatos del Expediente
                </h3>
                <button @click="metadataModal = false" class="text-slate-400 hover:text-red-500"><svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg></button>
            </div>
            <div class="p-6 space-y-4">
                <div class="grid grid-cols-2 gap-4">
                    <div class="bg-slate-50 p-3 rounded-xl border border-slate-100">
                        <p class="text-xs text-slate-400 font-bold mb-1">CÓDIGO TRD</p>
                        <p class="text-sm font-mono text-slate-700 font-bold break-all">{{ exp.codigo_expediente }}</p>
                    </div>
                    <div class="bg-slate-50 p-3 rounded-xl border border-slate-100">
                        <p class="text-xs text-slate-400 font-bold mb-1">NOMBRE</p>
                        <p class="text-sm text-slate-700 font-bold">{{ exp.nombre_expediente }}</p>
                    </div>
                    <div class="bg-slate-50 p-3 rounded-xl border border-slate-100">
                        <p class="text-xs text-slate-400 font-bold mb-1">ESTADO</p>
                        <p class="text-sm text-slate-700 font-bold">{% if exp.estado_abierto %}ABIERTO{% else %}CERRADO{% endif %}</p>
                    </div>
                    <div class="bg-slate-50 p-3 rounded-xl border border-slate-100">
                        <p class="text-xs text-slate-400 font-bold mb-1">FECHA APERTURA</p>
                        <p class="text-sm text-slate-700 font-bold">{{ exp.fecha_apertura }}</p>
                    </div>
                    <div class="bg-slate-50 p-3 rounded-xl border border-slate-100">
                        <p class="text-xs text-slate-400 font-bold mb-1">RESPONSABLE (USUARIO)</p>
                        <p class="text-sm text-slate-700 font-bold">{{ exp.responsable_id }}</p>
                    </div>
                    <div class="bg-slate-50 p-3 rounded-xl border border-slate-100">
                        <p class="text-xs text-slate-400 font-bold mb-1">AÑO FISCAL</p>
                        <p class="text-sm text-slate-700 font-bold">{{ exp.anio }}</p>
                    </div>
                </div>
                <div class="bg-slate-50 p-3 rounded-xl border border-slate-100">
                    <p class="text-xs text-slate-400 font-bold mb-1">ASUNTO / DESCRIPCIÓN</p>
                    <p class="text-sm text-slate-700">{{ exp.asunto or 'Sin descripción adicional' }}</p>
                </div>
            </div>
            <div class="px-6 py-4 border-t border-slate-100 bg-slate-50 flex justify-end">
                <button @click="metadataModal = false" class="px-6 py-2 bg-indigo-600 text-white font-bold rounded-xl hover:bg-indigo-700 transition-colors">Cerrar</button>
            </div>
        </div>
    </div>
"""
content = content.replace('<!-- Modal: Vincular Documento -->', new_modals + '\n    <!-- Modal: Vincular Documento -->')

js_add = """
        function showTxInfo(hash, accion, fecha, usuario, doc_id) {
            Swal.fire({
                title: 'Detalle Criptográfico',
                html: `
                    <div class="text-left space-y-3 mt-4 text-sm">
                        <div class="bg-slate-50 p-3 rounded-lg border border-slate-200">
                            <span class="text-xs font-bold text-slate-400 block mb-1">ACCIÓN:</span>
                            <span class="font-bold text-indigo-600">${accion}</span>
                        </div>
                        <div class="bg-slate-50 p-3 rounded-lg border border-slate-200">
                            <span class="text-xs font-bold text-slate-400 block mb-1">FECHA DEL EVENTO:</span>
                            <span class="font-bold text-slate-700">${fecha}</span>
                        </div>
                        <div class="bg-slate-50 p-3 rounded-lg border border-slate-200">
                            <span class="text-xs font-bold text-slate-400 block mb-1">AUTORIZADO POR (ID):</span>
                            <span class="font-mono text-slate-700 break-all text-xs">${usuario}</span>
                        </div>
                        <div class="bg-slate-50 p-3 rounded-lg border border-slate-200">
                            <span class="text-xs font-bold text-slate-400 block mb-1">DOCUMENTO AFECTADO (SI APLICA):</span>
                            <span class="font-mono text-slate-700 break-all text-xs">${doc_id}</span>
                        </div>
                        <div class="bg-indigo-50 p-3 rounded-lg border border-indigo-100">
                            <span class="text-xs font-bold text-indigo-400 block mb-1">HASH DE TRANSACCIÓN (SHA-256):</span>
                            <span class="font-mono text-indigo-700 break-all text-[11px]">${hash}</span>
                        </div>
                    </div>
                `,
                width: 600,
                confirmButtonText: 'Cerrar Inspector',
                confirmButtonColor: '#4f46e5'
            });
        }
"""
content = content.replace("function cerrarExpediente() {", js_add + "\n        function cerrarExpediente() {")

with open("app/templates/pages/expediente_view.html", "w", encoding="utf-8") as f:
    f.write(content)
