with open("app/templates/components/explorer.html", "r", encoding="utf-8") as f:
    content = f.read()

import re
old_tabs = """      <section class="mb-8" x-data="{ dragHover: null, tab: 'carpetas' }">
          <div class="flex justify-between items-end mb-4">
              <div class="flex items-center gap-4">
                  <div class="flex items-center gap-6 border-b border-gray-200">
                      <button type="button" @click="tab = 'carpetas'" :class="tab === 'carpetas' ? 'text-primary border-primary' : 'text-gray-400 border-transparent hover:text-gray-600'" class="text-xl font-bold pb-2 border-b-2 transition-colors">Carpetas</button>
                      <button type="button" @click="tab = 'expedientes'" hx-get="/api/v1/agn/expedientes/explorer" hx-target="#expedientes-grid" :class="tab === 'expedientes' ? 'text-primary border-primary' : 'text-gray-400 border-transparent hover:text-gray-600'" class="text-xl font-bold pb-2 border-b-2 transition-colors">Expedientes</button>
                  </div>
                  <button x-show="activeFolder !== ''" @click="activeFolder = ''; document.querySelector('input[name=folder_filter]').value = ''; htmx.trigger('#explorer-search-input', 'search')" class="flex items-center gap-1 px-3 py-1 bg-red-50 text-red-600 rounded-lg text-sm font-medium hover:bg-red-100 transition-colors">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
                      Volver a todos
                  </button>
              </div>
              <button class="text-primary font-medium hover:underline text-sm">Ver todo</button>
          </div>
          
          <div x-show="tab === 'carpetas'">"""

new_tabs = """      <section class="mb-8" x-data="{ dragHover: null }">
          <div class="flex justify-between items-end mb-4">
              <div class="flex items-center gap-4">
                  <div class="flex items-center gap-6 border-b border-gray-200">
                      <h2 class="text-xl font-bold pb-2 border-b-2 border-primary text-primary">Carpetas</h2>
                  </div>
                  <button x-show="activeFolder !== ''" @click="activeFolder = ''; document.querySelector('input[name=folder_filter]').value = ''; htmx.trigger('#explorer-search-input', 'search')" class="flex items-center gap-1 px-3 py-1 bg-red-50 text-red-600 rounded-lg text-sm font-medium hover:bg-red-100 transition-colors">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
                      Volver a todos
                  </button>
              </div>
              <button class="text-primary font-medium hover:underline text-sm">Ver todo</button>
          </div>
          
          <div>"""

content = content.replace(old_tabs, new_tabs)
content = content.replace("""          <div x-show="tab === 'expedientes'" x-cloak>
              <div id="expedientes-grid" class="mb-8">
                  <!-- HTMX will load the expedientes list here -->
              </div>
          </div>""", "")

with open("app/templates/components/explorer.html", "w", encoding="utf-8") as f:
    f.write(content)
