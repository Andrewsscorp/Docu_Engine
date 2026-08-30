with open("app/templates/pages/expediente_view.html", "r", encoding="utf-8") as f:
    content = f.read()

# Add th for Opciones
old_thead = """<th scope="col" class="px-6 py-4 font-bold tracking-wider">NOMBRE</th>
                            </tr>"""
new_thead = """<th scope="col" class="px-6 py-4 font-bold tracking-wider">NOMBRE</th>
                                <th scope="col" class="px-6 py-4 font-bold tracking-wider text-right">OPCIONES</th>
                            </tr>"""
content = content.replace(old_thead, new_thead)

# Add td with buttons
old_td = """<span class="truncate max-w-xs">{{ doc.file_name }}</span>
                                </td>
                            </tr>"""
new_td = """<span class="truncate max-w-xs">{{ doc.file_name }}</span>
                                </td>
                                <td class="px-6 py-4 text-right">
                                    <div class="flex items-center justify-end gap-2">
                                        <button @click.stop="$dispatch('open-drawer', '{{ doc.id }}')" class="p-2 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors tooltip" title="Ver Documento">
                                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
                                        </button>
                                        <button @click.stop="window.location.href = '/api/v1/documents/{{ doc.id }}/download'" class="p-2 text-slate-400 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors tooltip" title="Descargar PDF">
                                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                                        </button>
                                    </div>
                                </td>
                            </tr>"""
content = content.replace(old_td, new_td)

old_colspan = '<td colspan="4"'
new_colspan = '<td colspan="5"'
content = content.replace(old_colspan, new_colspan)

with open("app/templates/pages/expediente_view.html", "w", encoding="utf-8") as f:
    f.write(content)
