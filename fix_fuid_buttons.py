with open("app/templates/pages/fuid_view.html", "r", encoding="utf-8") as f:
    content = f.read()

# Update Firmar y Exportar FUID button
old_btn = """<button class="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-xl shadow-md transition-all flex items-center font-bold text-sm tracking-wide gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
                Firmar y Exportar FUID
            </button>"""

new_btn = """<button hx-post="/api/v1/agn/subseries/{{ subserie.id }}/fuid/firmar"
                    hx-swap="none"
                    class="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-xl shadow-md transition-all flex items-center font-bold text-sm tracking-wide gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
                Firmar y Exportar FUID
            </button>
            <script>
                document.body.addEventListener('htmx:afterRequest', function(evt) {
                    if (evt.detail.elt.getAttribute('hx-post') && evt.detail.elt.getAttribute('hx-post').includes('firmar')) {
                        if(evt.detail.successful) {
                            let data = JSON.parse(evt.detail.xhr.response);
                            if(data.status === 'success') {
                                Swal.fire('¡Transferencia Completada!', 'El FUID fue firmado y cerrado criptográficamente.\\nHash: ' + data.hash, 'success').then(() => {
                                    window.location.reload();
                                });
                            } else {
                                Swal.fire('Error', data.detail, 'error');
                            }
                        } else {
                            Swal.fire('Error de Firma', 'Ocurrió un error al procesar el cierre.', 'error');
                        }
                    }
                });
            </script>"""

content = content.replace(old_btn, new_btn)

# Update CSV button
old_csv_btn = """<button class="p-2 text-slate-500 hover:bg-slate-100 rounded-lg transition-colors border border-slate-200 tooltip" title="Descargar plano (CSV)">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                </button>"""

new_csv_btn = """<a href="/api/v1/agn/subseries/{{ subserie.id }}/fuid/csv" target="_blank" class="p-2 text-slate-500 hover:bg-slate-100 rounded-lg transition-colors border border-slate-200 tooltip" title="Descargar plano (CSV)">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                </a>"""
                
content = content.replace(old_csv_btn, new_csv_btn)

with open("app/templates/pages/fuid_view.html", "w", encoding="utf-8") as f:
    f.write(content)
