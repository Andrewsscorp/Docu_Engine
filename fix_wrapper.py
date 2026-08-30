with open("app/templates/components/explorer.html", "r", encoding="utf-8") as f:
    content = f.read()

# Replace <div class="grid grid-cols-1 md:grid-cols-3 gap-4"> with the wrapper
old_grid = '<div class="grid grid-cols-1 md:grid-cols-3 gap-4">'
new_grid = """
        <div x-show="tab === 'carpetas'">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
"""
content = content.replace(old_grid, new_grid)

# Find {% endif %} right after {% if not folders %} and end the wrapper
old_endif = """            {% if not folders %}
            <div class="col-span-full py-8 text-center text-gray-400 text-sm border-2 border-dashed border-gray-200 rounded-2xl">
                Aún no tienes carpetas. Haz clic en "Nueva Carpeta" para crear una.
            </div>
            {% endif %}
        </div>
        
        window.openMoveModal"""

new_endif = """            {% if not folders %}
            <div class="col-span-full py-8 text-center text-gray-400 text-sm border-2 border-dashed border-gray-200 rounded-2xl">
                Aún no tienes carpetas. Haz clic en "Nueva Carpeta" para crear una.
            </div>
            {% endif %}
            </div>
        </div>

        <div x-show="tab === 'expedientes'" x-cloak>
            <div id="expedientes-grid" class="mb-8">
                <!-- HTMX will load the expedientes list here -->
            </div>
        </div>
        
        window.openMoveModal"""

content = content.replace(old_endif, new_endif)

with open("app/templates/components/explorer.html", "w", encoding="utf-8") as f:
    f.write(content)
