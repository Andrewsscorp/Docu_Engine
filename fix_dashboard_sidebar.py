with open("app/templates/pages/dashboard.html", "r", encoding="utf-8") as f:
    content = f.read()

import re

old_sidebar_docs = """          <li @click="currentView = 'explorer'" title="Documentos"
              class="px-5 py-3.5 rounded-2xl cursor-pointer font-medium transition-all flex items-center gap-4 whitespace-nowrap overflow-hidden"
              :class="currentView === 'explorer' ? 'bg-gradient-to-r from-primary to-[#868CFF] text-white shadow-lg shadow-primary/40' : 'text-gray-400 hover:text-white hover:bg-white/5'">
              <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"></path></svg>
              <span x-show="sidebarOpen" x-transition.opacity>Documentos</span>
          </li>"""

new_sidebar_docs = """          <li @click="currentView = 'explorer'" title="Documentos"
              class="px-5 py-3.5 rounded-2xl cursor-pointer font-medium transition-all flex items-center gap-4 whitespace-nowrap overflow-hidden"
              :class="currentView === 'explorer' ? 'bg-gradient-to-r from-primary to-[#868CFF] text-white shadow-lg shadow-primary/40' : 'text-gray-400 hover:text-white hover:bg-white/5'">
              <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"></path></svg>
              <span x-show="sidebarOpen" x-transition.opacity>Documentos</span>
          </li>
          <li @click="currentView = 'expedientes_module'" title="Expedientes"
              class="px-5 py-3.5 rounded-2xl cursor-pointer font-medium transition-all flex items-center gap-4 whitespace-nowrap overflow-hidden"
              :class="currentView === 'expedientes_module' ? 'bg-gradient-to-r from-primary to-[#868CFF] text-white shadow-lg shadow-primary/40' : 'text-gray-400 hover:text-white hover:bg-white/5'">
              <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"></path></svg>
              <span x-show="sidebarOpen" x-transition.opacity>Expedientes</span>
          </li>"""

content = content.replace(old_sidebar_docs, new_sidebar_docs)

# Add the title change
content = content.replace(
    "currentView === 'tags' ? 'Gestin de Etiquetas' : (currentView === 'expediente' ? 'Expediente Electrnico'",
    "currentView === 'tags' ? 'Gestión de Etiquetas' : (currentView === 'expedientes_module' ? 'Expedientes SGDEA' : (currentView === 'expediente' ? 'Expediente Electrónico'"
)

# Add the new section container
old_explorer_section = """<!-- EXPLORER VIEW -->
<section class="min-w-0 w-full flex-1 flex flex-col" x-show="currentView === 'explorer'" x-transition.opacity.duration.300ms x-cloak>
    <div hx-get="/api/v1/documents/explorer" hx-trigger="load, reloadExplorer from:body">
        <div class="flex justify-center items-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
    </div>
</section>"""

new_explorer_section = """<!-- EXPLORER VIEW -->
<section class="min-w-0 w-full flex-1 flex flex-col" x-show="currentView === 'explorer'" x-transition.opacity.duration.300ms x-cloak>
    <div hx-get="/api/v1/documents/explorer" hx-trigger="load, reloadExplorer from:body">
        <div class="flex justify-center items-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
    </div>
</section>

<!-- EXPEDIENTES MODULE VIEW -->
<section class="min-w-0 w-full flex-1 flex flex-col" x-show="currentView === 'expedientes_module'" x-transition.opacity.duration.300ms x-cloak>
    <div hx-get="/api/v1/agn/expedientes/module" hx-trigger="load, reloadExpedientes from:body">
        <div class="flex justify-center items-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
    </div>
</section>"""

content = content.replace(old_explorer_section, new_explorer_section)

with open("app/templates/pages/dashboard.html", "w", encoding="utf-8") as f:
    f.write(content)
