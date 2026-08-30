with open("app/templates/components/expedientes_grid_items.html", "r", encoding="utf-8") as f:
    content = f.read()

old_buttons = """        <div class="flex gap-4 text-gray-400">
            {% if exp.estado_abierto and exp.fase_archivo != 'TRANSFERENCIA' %}
            <!-- Edit Button -->"""

new_buttons = """        <div class="flex gap-4 text-gray-400">
            <!-- Info Button -->
            <button class="hover:text-indigo-600 transition-colors z-10" title="Ver Metadatos Completos"
                    onclick="verMetadatos('{{exp.id}}')">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            </button>
            {% if exp.estado_abierto and exp.fase_archivo != 'TRANSFERENCIA' %}
            <!-- Edit Button -->"""

content = content.replace(old_buttons, new_buttons)

with open("app/templates/components/expedientes_grid_items.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Added info button to HTML")
