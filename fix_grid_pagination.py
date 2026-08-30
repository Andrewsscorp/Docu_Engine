with open("app/templates/components/expedientes_grid.html", "w", encoding="utf-8") as f:
    f.write("""<div id="expedientes-grid-wrapper" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4" x-bind:class="viewMode === 'list' ? 'grid-cols-1 md:grid-cols-1 lg:grid-cols-1' : 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4'">
    {% include 'components/expedientes_grid_items.html' %}
    
    {% if not expedientes and page == 1 %}
    <div class="col-span-full py-16 text-center bg-white rounded-2xl border border-dashed border-gray-300">
        <svg class="w-12 h-12 text-gray-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"></path></svg>
        <h3 class="text-gray-500 font-medium">No hay expedientes que coincidan con los filtros</h3>
        <p class="text-sm text-gray-400 mt-1">Intenta ajustando tu búsqueda o filtros.</p>
    </div>
    {% endif %}
</div>
<script>
    document.getElementById('total-expedientes-badge').innerText = "{{ total_count|default(0) }} Total";
</script>""")

with open("app/templates/components/expedientes_grid_items.html", "r", encoding="utf-8") as f:
    items = f.read()

# Modify the button logic
import re
old_button = r"{% if has_more %}.*?{% endif %}"
new_button = """{% if has_more %}
<div id="expedientes-load-more" class="col-span-full flex justify-center py-6">
    <button hx-get="/api/v1/agn/expedientes/module?page={{ page + 1 }}" 
            hx-include="[name='q'], [name='status'], [name='subserie_id'], [name='fecha_inicio'], [name='fecha_fin'], [name='soporte']" 
            hx-target="#expedientes-load-more" 
            hx-swap="outerHTML"
            hx-indicator="#load-more-spinner"
            onclick="this.style.display='none'"
            class="px-5 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors shadow-sm">
        Cargar más expedientes
    </button>
    <div id="load-more-spinner" class="htmx-indicator animate-spin rounded-full h-6 w-6 border-b-2 border-primary hidden"></div>
</div>
{% endif %}"""

items = re.sub(old_button, new_button, items, flags=re.DOTALL)
with open("app/templates/components/expedientes_grid_items.html", "w", encoding="utf-8") as f:
    f.write(items)
