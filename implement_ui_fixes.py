with open("app/templates/pages/fuid_view.html", "r", encoding="utf-8") as f:
    content = f.read()

import re

# 1. Update the Firmar y Exportar button to use a native JS/Alpine function for the Swal popup and fetch
firmar_pattern = r'<button class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2.5 px-6 rounded-xl shadow-md\s+shadow-indigo-200 transition-all flex items-center gap-2">.*?Firmar y Exportar FUID\s+</button>'
new_firmar = """<button @click="firmarFUID('{{ subserie.id }}')" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2.5 px-6 rounded-xl shadow-md shadow-indigo-200 transition-all flex items-center gap-2">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
                  Firmar y Exportar FUID
              </button>"""
content = re.sub(firmar_pattern, new_firmar, content, flags=re.DOTALL)

# 2. Update the main container to include Alpine x-data for columns
xdata_pattern = r'<div class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">'
new_xdata = """<div class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden" 
     x-data="{ 
         cols: {
             orden: true,
             codigo: true,
             nombre: true,
             fechas: true,
             caja: true,
             folios: true,
             soporte: true,
             acciones: true
         },
         showColMenu: false,
         firmarFUID(subserieId) {
             Swal.fire({
                 title: '¿Confirmar Firma Criptográfica?',
                 text: 'Esta acción aplicará un sello SHA-256 al Formato Único de Inventario Documental. Los expedientes pasarán a Archivo Central y no podrán ser modificados. Esta acción es inmutable según la Ley 527 de 1999.',
                 icon: 'warning',
                 showCancelButton: true,
                 confirmButtonColor: '#4f46e5',
                 cancelButtonColor: '#ef4444',
                 confirmButtonText: 'Sí, Firmar y Exportar',
                 cancelButtonText: 'Cancelar'
             }).then((result) => {
                 if (result.isConfirmed) {
                     Swal.fire({title: 'Firmando...', text: 'Generando PDF/A e inyectando Hash...', allowOutsideClick: false, didOpen: () => { Swal.showLoading() }});
                     fetch('/api/v1/agn/subseries/' + subserieId + '/fuid/firmar', {
                         method: 'POST',
                         headers: { 'Content-Type': 'application/json' }
                     })
                     .then(res => res.json())
                     .then(data => {
                         if(data.status === 'success') {
                             Swal.fire('¡Transferencia Completada!', 'El FUID fue firmado criptográficamente.\\nHash: ' + data.hash, 'success').then(() => {
                                 window.open('/api/v1/agn/fuid/descargar_pdf/' + data.hash, '_blank');
                                 setTimeout(() => window.location.reload(), 1000);
                             });
                         } else {
                             Swal.fire('Error', data.detail || 'Ocurrió un error en la base de datos.', 'error');
                         }
                     })
                     .catch(err => {
                         Swal.fire('Error', 'Fallo de red.', 'error');
                     });
                 }
             });
         }
     }">"""
content = content.replace(xdata_pattern, new_xdata)

# 3. Update the Toolbars for Column Visibility and CSV Download
toolbar_pattern = r'<div class="flex items-center gap-2">\s+<button class="p-2 text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg border\s+border-slate-200 bg-white transition-colors">\s+<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path\s+stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0\s+012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0\s+002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2"></path></svg>\s+</button>\s+<button class="p-2 text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg border\s+border-slate-200 bg-white transition-colors">\s+<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path\s+stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0\s+0l-4-4m4 4V4"></path></svg>\s+</button>\s+</div>'

new_toolbar = """<div class="flex items-center gap-2">
              <div class="relative">
                  <button @click="showColMenu = !showColMenu" @click.away="showColMenu = false" class="p-2 text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg border border-slate-200 bg-white transition-colors tooltip" title="Visibilidad de Columnas">
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2"></path></svg>
                  </button>
                  
                  <div x-show="showColMenu" x-transition class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-xl border border-slate-200 z-50 p-2">
                      <div class="text-xs font-bold text-slate-400 mb-2 px-2">MOSTRAR COLUMNAS</div>
                      <label class="flex items-center px-2 py-1 hover:bg-slate-50 cursor-pointer rounded"><input type="checkbox" x-model="cols.orden" class="mr-2 rounded text-indigo-600 focus:ring-indigo-500"> No. Orden</label>
                      <label class="flex items-center px-2 py-1 hover:bg-slate-50 cursor-pointer rounded"><input type="checkbox" x-model="cols.codigo" class="mr-2 rounded text-indigo-600 focus:ring-indigo-500"> Código</label>
                      <label class="flex items-center px-2 py-1 hover:bg-slate-50 cursor-pointer rounded"><input type="checkbox" x-model="cols.nombre" class="mr-2 rounded text-indigo-600 focus:ring-indigo-500"> Nombre Unidad</label>
                      <label class="flex items-center px-2 py-1 hover:bg-slate-50 cursor-pointer rounded"><input type="checkbox" x-model="cols.fechas" class="mr-2 rounded text-indigo-600 focus:ring-indigo-500"> Fechas</label>
                      <label class="flex items-center px-2 py-1 hover:bg-slate-50 cursor-pointer rounded"><input type="checkbox" x-model="cols.caja" class="mr-2 rounded text-indigo-600 focus:ring-indigo-500"> Caja/Carpeta</label>
                      <label class="flex items-center px-2 py-1 hover:bg-slate-50 cursor-pointer rounded"><input type="checkbox" x-model="cols.folios" class="mr-2 rounded text-indigo-600 focus:ring-indigo-500"> Folios</label>
                      <label class="flex items-center px-2 py-1 hover:bg-slate-50 cursor-pointer rounded"><input type="checkbox" x-model="cols.soporte" class="mr-2 rounded text-indigo-600 focus:ring-indigo-500"> Soporte</label>
                  </div>
              </div>
              
              <a href="/api/v1/agn/subseries/{{ subserie.id }}/fuid/csv" target="_blank" class="p-2 text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg border border-slate-200 bg-white transition-colors tooltip" title="Descarga Plana de Trabajo (Borrador)">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
              </a>
          </div>"""
content = re.sub(toolbar_pattern, new_toolbar, content, flags=re.DOTALL)

# 4. Update Table Headers with x-show
th_orden = r'<th class="px-6 py-4 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">\s+NO\.\s+ORDEN\s+</th>'
content = re.sub(th_orden, '<th x-show="cols.orden" class="px-6 py-4 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">\n                        NO. ORDEN\n                    </th>', content)

th_codigo = r'<th class="px-6 py-4 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">\s+CÓDIGO\s+</th>'
content = re.sub(th_codigo, '<th x-show="cols.codigo" class="px-6 py-4 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">\n                        CÓDIGO\n                    </th>', content)

th_nombre = r'<th class="px-6 py-4 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">\s+NOMBRE DE LA UNIDAD\s+DE CONSERVACIÓN\s+</th>'
content = re.sub(th_nombre, '<th x-show="cols.nombre" class="px-6 py-4 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">\n                        NOMBRE DE LA UNIDAD<br>DE CONSERVACIÓN\n                    </th>', content)

th_fechas = r'<th class="px-6 py-4 text-center text-xs font-bold text-slate-500 uppercase tracking-wider">\s+FECHAS EXTREMAS\s+<span class="block text-[10px] text-slate-400 font-normal lowercase">\(inicial - final\)</span>\s+</th>'
content = re.sub(th_fechas, '<th x-show="cols.fechas" class="px-6 py-4 text-center text-xs font-bold text-slate-500 uppercase tracking-wider">\n                        FECHAS EXTREMAS\n                        <span class="block text-[10px] text-slate-400 font-normal lowercase">(inicial - final)</span>\n                    </th>', content)

th_caja = r'<th class="px-6 py-4 text-center text-xs font-bold text-slate-500 uppercase tracking-wider">\s+CAJA/CARPETA\s+</th>'
content = re.sub(th_caja, '<th x-show="cols.caja" class="px-6 py-4 text-center text-xs font-bold text-slate-500 uppercase tracking-wider">\n                        CAJA/CARPETA\n                    </th>', content)

th_folios = r'<th class="px-6 py-4 text-center text-xs font-bold text-slate-500 uppercase tracking-wider">\s+FOLIOS\s+</th>'
content = re.sub(th_folios, '<th x-show="cols.folios" class="px-6 py-4 text-center text-xs font-bold text-slate-500 uppercase tracking-wider">\n                        FOLIOS\n                    </th>', content)

th_soporte = r'<th class="px-6 py-4 text-center text-xs font-bold text-slate-500 uppercase tracking-wider">\s+SOPORTE\s+</th>'
content = re.sub(th_soporte, '<th x-show="cols.soporte" class="px-6 py-4 text-center text-xs font-bold text-slate-500 uppercase tracking-wider">\n                        SOPORTE\n                    </th>', content)

th_acc = r'<th class="px-6 py-4 text-center text-xs font-bold text-slate-500 uppercase tracking-wider">\s+ACCIONES\s+</th>'
content = re.sub(th_acc, '<th x-show="cols.acciones" class="px-6 py-4 text-center text-xs font-bold text-slate-500 uppercase tracking-wider">\n                        ACCIONES\n                    </th>', content)

# 5. Update Table Cells with x-show
td_orden = r'<td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-indigo-600">\s+{{ r\.no_orden }}\s+</td>'
content = re.sub(td_orden, '<td x-show="cols.orden" class="px-6 py-4 whitespace-nowrap text-sm font-medium text-indigo-600">\n                            {{ r.no_orden }}\n                        </td>', content)

td_codigo = r'<td class="px-6 py-4 whitespace-nowrap text-sm font-mono text-slate-500">\s+{{ r\.codigo }}\s+</td>'
content = re.sub(td_codigo, '<td x-show="cols.codigo" class="px-6 py-4 whitespace-nowrap text-sm font-mono text-slate-500">\n                            {{ r.codigo }}\n                        </td>', content)

td_nombre = r'<td class="px-6 py-4 text-sm text-slate-900 font-medium">\s+{{ r\.nombre_unidad_conservacion }}\s+</td>'
content = re.sub(td_nombre, '<td x-show="cols.nombre" class="px-6 py-4 text-sm text-slate-900 font-medium">\n                            {{ r.nombre_unidad_conservacion }}\n                        </td>', content)

td_fechas = r'<td class="px-6 py-4 whitespace-nowrap text-center text-sm text-slate-500">\s+{% if r\.fecha_inicial_str %}\s+<span class="font-mono">{{ r\.fecha_inicial_str }}</span>\s+<span class="text-slate-300 mx-1">\|</span>\s+<span class="font-mono">{{ r\.fecha_final_str }}</span>\s+{% else %}\s+<span class="text-slate-400 italic">Sin documentos</span>\s+{% endif %}\s+</td>'
content = re.sub(td_fechas, '<td x-show="cols.fechas" class="px-6 py-4 whitespace-nowrap text-center text-sm text-slate-500">\n                            {% if r.fecha_inicial_str %}\n                            <span class="font-mono">{{ r.fecha_inicial_str }}</span>\n                            <span class="text-slate-300 mx-1">|</span>\n                            <span class="font-mono">{{ r.fecha_final_str }}</span>\n                            {% else %}\n                            <span class="text-slate-400 italic">Sin documentos</span>\n                            {% endif %}\n                        </td>', content)

td_caja = r'<td class="px-6 py-4 whitespace-nowrap text-center">\s+<div class="inline-flex items-center px-2\.5 py-1 rounded-md border border-slate-200 bg-slate-50 text-xs font-medium text-slate-600">\s+<svg class="w-3\.5 h-3\.5 mr-1\.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"></path></svg>\s+{{ r\.caja_carpeta }}\s+</div>\s+</td>'
content = re.sub(td_caja, '<td x-show="cols.caja" class="px-6 py-4 whitespace-nowrap text-center">\n                            <div class="inline-flex items-center px-2.5 py-1 rounded-md border border-slate-200 bg-slate-50 text-xs font-medium text-slate-600">\n                                <svg class="w-3.5 h-3.5 mr-1.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"></path></svg>\n                                {{ r.caja_carpeta }}\n                            </div>\n                        </td>', content)

td_folios = r'<td class="px-6 py-4 whitespace-nowrap text-center text-sm font-semibold text-slate-700">\s+{{ r\.folios }}\s+</td>'
content = re.sub(td_folios, '<td x-show="cols.folios" class="px-6 py-4 whitespace-nowrap text-center text-sm font-semibold text-slate-700">\n                            {{ r.folios }}\n                        </td>', content)

td_soporte = r'<td class="px-6 py-4 whitespace-nowrap text-center">\s+<span class="inline-flex items-center px-2\.5 py-0\.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">\s+{{ r\.soporte }}\s+</span>\s+</td>'
content = re.sub(td_soporte, '<td x-show="cols.soporte" class="px-6 py-4 whitespace-nowrap text-center">\n                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">\n                                {{ r.soporte }}\n                            </span>\n                        </td>', content)

td_acc = r'<td class="px-6 py-4 whitespace-nowrap text-center text-sm font-medium">\s+<button class="text-slate-400 hover:text-indigo-600 transition-colors tooltip" title="Ver Expediente">\s+<svg class="w-5 h-5 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2\.458 12C3\.732 7\.943 7\.523 5 12 5c4\.478 0 8\.268 2\.943 9\.542 7-1\.274 4\.057-5\.064 7-9\.542 7-4\.477 0-8\.268-2\.943-9\.542-7z"></path></svg>\s+</button>\s+</td>'
content = re.sub(td_acc, '<td x-show="cols.acciones" class="px-6 py-4 whitespace-nowrap text-center text-sm font-medium">\n                            <button class="text-slate-400 hover:text-indigo-600 transition-colors tooltip" title="Ver Expediente">\n                                <svg class="w-5 h-5 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>\n                            </button>\n                        </td>', content)

with open("app/templates/pages/fuid_view.html", "w", encoding="utf-8") as f:
    f.write(content)
