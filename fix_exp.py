with open("expediente_view_old.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update x-data
content = content.replace(
    'x-data="{ addDocModal: false, metadataModal: false, selectedDoc: \'\', selectedTipo: \'\' }"',
    'x-data="{ addDocModal: false, metadataModal: false, selectedDoc: \'\', selectedTipo: \'\', visorAbierto: false, visorPdfUrl: \'\', mostrarFiltro: false, filtroDoc: \'\' }"'
)

# 2. Add filter to the Documentos PDF header
old_header = """<div class="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50">
                    <h3 class="font-bold text-slate-800 flex items-center gap-2">
                        Documentos PDF <span class="px-2 py-0.5 bg-slate-200 text-slate-600 rounded-full text-xs">{{ docs|length }} items</span>
                    </h3>
                </div>"""
new_header = """<div class="px-6 py-4 border-b border-slate-100 flex flex-col gap-3 bg-slate-50">
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
content = content.replace(old_header, new_header)

# 3. Add x-show to TR
old_tr = '<tr class="bg-white border-b border-slate-50 hover:bg-slate-50/50 transition-colors">'
new_tr = '<tr class="bg-white border-b border-slate-50 hover:bg-slate-50/50 transition-colors" x-show="filtroDoc === \'\' || \'{{ doc.file_name | lower }} {{ doc.tipo_nombre | lower }}\'.includes(filtroDoc.toLowerCase())">'
content = content.replace(old_tr, new_tr)

# 4. Add eye icon to Opciones column
old_td_end = """                                </td>
                            </tr>"""
new_td_end = """                                        <button @click.stop="visorPdfUrl = '/api/v1/agn/documentos/{{ doc.id }}/ver_forense'; visorAbierto = true;" class="p-2 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors tooltip" title="Visor Forense">
                                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
                                        </button>
                                        <button @click.stop="Swal.fire({toast:true, position:'top-end', icon:'info', title:'Descarga Forense Iniciada...', showConfirmButton:false, timer:2000}); window.location.href = '/api/v1/agn/documentos/{{ doc.id }}/descargar_forense';" class="p-2 text-slate-400 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors tooltip" title="Descarga Física">
                                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                                        </button>
                                    </div>
                                </td>
                            </tr>"""

# wait! how is old_td_end structured in the old file? let's check first!
