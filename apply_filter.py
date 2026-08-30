with open("app/templates/pages/expediente_view.html", "r", encoding="utf-8") as f:
    original = f.read()

old_header = """                <div class="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50">
                    <h3 class="font-bold text-slate-800 flex items-center gap-2">
                        Documentos PDF <span class="px-2 py-0.5 bg-slate-200 text-slate-600 rounded-full text-xs">{{ docs|length }} items</span>
                    </h3>
                    <div class="flex gap-2">
                        <button class="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"></path></svg></button>
                        <button class="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg></button>
                    </div>
                </div>"""

new_header = """                <div class="px-6 py-4 border-b border-slate-100 flex flex-col gap-3 bg-slate-50">
                    <div class="flex justify-between items-center w-full">
                        <h3 class="font-bold text-slate-800 flex items-center gap-2">
                            Documentos PDF <span class="px-2 py-0.5 bg-slate-200 text-slate-600 rounded-full text-xs">{{ docs|length }} items</span>
                        </h3>
                        <div class="flex gap-2">
                            <button @click="mostrarFiltro = !mostrarFiltro" class="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors tooltip" title="Filtro de Metadatos">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"></path></svg>
                            </button>
                            <button @click="Swal.fire({title: 'Empaquetando DIP', text: 'Compilando PDFs e Índice XML...', allowOutsideClick: false, didOpen: () => Swal.showLoading()}); window.location.href = '/api/v1/agn/expedientes/{{ exp.id }}/exportar'; setTimeout(() => Swal.close(), 4000);" class="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors tooltip" title="Exportación Masiva (DIP)">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                            </button>
                        </div>
                    </div>
                    <div x-show="mostrarFiltro" x-collapse>
                        <input type="text" x-model="filtroDoc" placeholder="Filtrar por nombre o tipología..." class="w-full px-4 py-2 bg-white border border-slate-200 rounded-lg text-sm outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500">
                    </div>
                </div>"""

original = original.replace(old_header, new_header)

with open("app/templates/pages/expediente_view.html", "w", encoding="utf-8") as f:
    f.write(original)
