with open("app/templates/components/expedientes_grid_items.html", "r", encoding="utf-8") as f:
    content = f.read()

# Make card clickable
content = content.replace(
    '<div class="card bg-white',
    '<div @click="if (!$event.target.closest(\'button\')) { currentView = \'expediente\'; htmx.ajax(\'GET\', \'/api/v1/agn/expedientes/{{exp.id}}/view\', {target: \'#expediente-inner-container\'}) }" class="card cursor-pointer bg-white'
)

# Add soporte
soporte_li = """        <li class="flex items-center gap-2">
            <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"></path></svg> 
            Soporte: <span class="font-medium text-gray-700">{{ exp.soporte|capitalize }}</span>
        </li>"""
content = content.replace(
    'Resp: <span class="truncate max-w-[150px]">{{ exp.responsable_nombre or \'Sin Asignar\' }}</span>\n        </li>',
    'Resp: <span class="truncate max-w-[150px]">{{ exp.responsable_nombre or \'Sin Asignar\' }}</span>\n        </li>\n' + soporte_li
)

# Change shield icon to lock and hide buttons if not open
old_buttons = """        <div class="flex gap-4 text-gray-400">
            <!-- Edit Button -->
            <button class="hover:text-blue-600 transition-colors" title="Editar Metadatos"
                    onclick="editExpediente('{{exp.id}}', '{{exp.nombre_expediente}}', {{ 'true' if exp.estado_abierto and exp.fase_archivo != 'TRANSFERENCIA' else 'false' }})">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
            </button>
            <!-- Seal/Close Button -->
            <button class="hover:text-green-600 transition-colors" title="Cerrar Expediente / Iniciar Retencin"
                    onclick="cerrarExpediente('{{exp.id}}')">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path></svg>
            </button>
        </div>"""

new_buttons = """        <div class="flex gap-4 text-gray-400">
            {% if exp.estado_abierto and exp.fase_archivo != 'TRANSFERENCIA' %}
            <!-- Edit Button -->
            <button class="hover:text-blue-600 transition-colors z-10" title="Editar Metadatos"
                    onclick="editExpediente('{{exp.id}}', '{{exp.nombre_expediente}}', '{{exp.soporte}}')">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
            </button>
            <!-- Seal/Close Button -->
            <button class="hover:text-red-600 transition-colors z-10" title="Cerrar Expediente / Iniciar Retención"
                    onclick="cerrarExpediente('{{exp.id}}')">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
            </button>
            {% endif %}
        </div>"""
content = content.replace(old_buttons, new_buttons)

with open("app/templates/components/expedientes_grid_items.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated grid items html")
