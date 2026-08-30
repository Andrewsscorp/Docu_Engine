with open("app/templates/pages/dashboard.html", "r", encoding="utf-8") as f:
    content = f.read()

import re

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

content = re.sub(r"<li @click=\"currentView = 'explorer'\".*?</li>", new_sidebar_docs, content, flags=re.DOTALL)

# Also fix the title rendering in the header
title_replace = "currentView === 'tags' ? 'Gestin de Etiquetas' : (currentView === 'expedientes_module' ? 'Expedientes SGDEA' : (currentView === 'expediente' ? 'Expediente Electrnico'"

# Actually, the original is: currentView === 'tags' ? 'Gestin de Etiquetas' : (currentView === 'expediente' ? 'Expediente Electrnico'
# Just use a safer replacement pattern
content = re.sub(
    r"currentView === 'tags' \? '(.*?)' : \(currentView === 'expediente'",
    r"currentView === 'tags' ? '\1' : (currentView === 'expedientes_module' ? 'Expedientes SGDEA' : (currentView === 'expediente'",
    content
)

with open("app/templates/pages/dashboard.html", "w", encoding="utf-8") as f:
    f.write(content)
