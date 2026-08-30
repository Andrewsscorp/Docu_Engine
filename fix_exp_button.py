with open("app/templates/components/expedientes_module.html", "r", encoding="utf-8") as f:
    content = f.read()

import re

old_header = """        <div class="flex gap-3">
            <select name="status" class="bg-white border border-gray-200 text-gray-700 text-sm rounded-xl focus:ring-primary focus:border-primary block p-2.5 card-shadow"
                    hx-get="/api/v1/agn/expedientes/module"
                    hx-trigger="change"
                    hx-target="#expedientes-results-grid"
                    hx-include="[name='q']">
                <option value="" {% if not status %}selected{% endif %}>Todos los Estados</option>
                <option value="abierto" {% if status == 'abierto' %}selected{% endif %}>ABIERTO</option>
                <option value="cerrado" {% if status == 'cerrado' %}selected{% endif %}>CERRADO</option>
            </select>
        </div>"""

new_header = """        <div class="flex gap-3">
            <select name="status" class="bg-white border border-gray-200 text-gray-700 text-sm font-medium rounded-xl focus:ring-primary focus:border-primary block p-2.5 card-shadow"
                    hx-get="/api/v1/agn/expedientes/module"
                    hx-trigger="change"
                    hx-target="#expedientes-results-grid"
                    hx-include="[name='q']">
                <option value="" {% if not status %}selected{% endif %}>Todos los Estados</option>
                <option value="abierto" {% if status == 'abierto' %}selected{% endif %}>Abierto</option>
                <option value="cerrado" {% if status == 'cerrado' %}selected{% endif %}>Cerrado</option>
            </select>
            
            <button type="button" onclick="window.openAgnModal()" class="bg-primary hover:bg-blue-700 text-white font-bold py-2.5 px-6 rounded-xl transition-all shadow-lg shadow-primary/30 flex items-center gap-2 z-20 hover:scale-105 active:scale-95">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                Nuevo Expediente
            </button>
        </div>"""

content = content.replace(old_header, new_header)

with open("app/templates/components/expedientes_module.html", "w", encoding="utf-8") as f:
    f.write(content)
