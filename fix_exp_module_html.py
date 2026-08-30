with open("app/templates/components/expedientes_module.html", "r", encoding="utf-8") as f:
    content = f.read()

import re

# We will just rewrite the whole header section of the module
new_header = """<div class="px-8 pt-8 pb-6 bg-white/50 border-b border-gray-100 flex flex-col gap-6" x-data="{ viewMode: 'grid' }">
    <div class="flex justify-between items-end">
        <div>
            <h1 class="text-[28px] font-bold text-gray-900 leading-tight flex items-center gap-3">
                Gestión de Expedientes 
                <span id="total-expedientes-badge" class="text-xs font-semibold bg-gray-100 text-gray-500 px-2.5 py-1 rounded-full border border-gray-200">
                    {{ total_count|default(0) }} Total
                </span>
            </h1>
        </div>
        
        <button type="button" onclick="window.openAgnModal()" class="bg-primary hover:bg-blue-700 text-white font-bold py-2.5 px-6 rounded-xl transition-all shadow-lg shadow-primary/30 flex items-center gap-2 hover:scale-105 active:scale-95">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
            Nuevo Expediente
        </button>
    </div>

    <form id="expedientes-filters" class="flex flex-wrap items-center gap-3"
          hx-get="/api/v1/agn/expedientes/module" 
          hx-trigger="change, keyup delay:300ms from:input[name='q']" 
          hx-target="#expedientes-results-grid">
          
        <!-- Search -->
        <div class="relative flex-1 min-w-[250px]">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
            </div>
            <input type="text" name="q" value="{{ q|default('') }}" placeholder="Buscar por código, nombre..." 
                   class="w-full pl-10 pr-4 py-2.5 bg-white border border-gray-200 rounded-xl focus:ring-primary focus:border-primary text-sm shadow-sm transition-all outline-none">
        </div>

        <!-- Estado -->
        <select name="status" class="bg-white border border-gray-200 text-gray-700 text-sm font-medium rounded-xl focus:ring-primary focus:border-primary block p-2.5 shadow-sm min-w-[140px] outline-none">
            <option value="">Estado</option>
            <option value="abierto" {% if status == 'abierto' %}selected{% endif %}>Abierto</option>
            <option value="cerrado" {% if status == 'cerrado' %}selected{% endif %}>Cerrado</option>
            <option value="transferencia" {% if status == 'transferencia' %}selected{% endif %}>En Transferencia</option>
        </select>
        
        <!-- Fecha Rango (Simplified as inputs) -->
        <div class="flex items-center gap-2 bg-white border border-gray-200 rounded-xl p-1 shadow-sm">
            <input type="date" name="fecha_inicio" value="{{ fecha_inicio|default('') }}" class="text-sm text-gray-700 font-medium border-none focus:ring-0 px-2 py-1.5 outline-none rounded-lg bg-transparent" title="Fecha Inicio">
            <span class="text-gray-400">-</span>
            <input type="date" name="fecha_fin" value="{{ fecha_fin|default('') }}" class="text-sm text-gray-700 font-medium border-none focus:ring-0 px-2 py-1.5 outline-none rounded-lg bg-transparent" title="Fecha Fin">
        </div>
        
        <!-- Soporte -->
        <select name="soporte" class="bg-white border border-gray-200 text-gray-700 text-sm font-medium rounded-xl focus:ring-primary focus:border-primary block p-2.5 shadow-sm min-w-[140px] outline-none">
            <option value="">Soporte</option>
            <option value="ELECTRÓNICO" {% if soporte == 'ELECTRÓNICO' %}selected{% endif %}>Electrónico</option>
            <option value="FÍSICO" {% if soporte == 'FÍSICO' %}selected{% endif %}>Físico</option>
            <option value="HÍBRIDO" {% if soporte == 'HÍBRIDO' %}selected{% endif %}>Híbrido</option>
        </select>
        
        <!-- View Toggles (CSS Only) -->
        <div class="flex items-center bg-gray-100 p-1 rounded-xl border border-gray-200 ml-auto">
            <button type="button" @click="viewMode = 'grid'" :class="viewMode === 'grid' ? 'bg-white shadow-sm text-primary' : 'text-gray-500 hover:text-gray-700'" class="p-1.5 rounded-lg transition-all">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path></svg>
            </button>
            <button type="button" @click="viewMode = 'list'" :class="viewMode === 'list' ? 'bg-white shadow-sm text-primary' : 'text-gray-500 hover:text-gray-700'" class="p-1.5 rounded-lg transition-all">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"></path></svg>
            </button>
        </div>
    </form>
</div>

<div class="flex-1 overflow-y-auto p-8 relative scroll-smooth bg-slate-50/50">
    <!-- Spinner while HTMX is loading -->
    <div class="htmx-indicator absolute inset-0 bg-white/50 backdrop-blur-sm z-10 flex justify-center items-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>
    
    <div id="expedientes-results-grid">
        {% include 'components/expedientes_grid.html' %}
    </div>
</div>"""

# Find the entire structure and replace it
content = re.sub(r"<div class=\"px-8 pt-8 pb-6 bg-white/50.*$", new_header, content, flags=re.DOTALL)

with open("app/templates/components/expedientes_module.html", "w", encoding="utf-8") as f:
    f.write(content)
