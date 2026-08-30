with open("app/templates/components/explorer.html", "r", encoding="utf-8") as f:
    content = f.read()

import re

old_tabs = """      <section class="mb-8" x-data="{ dragHover: null, tab: 'carpetas' }">
          <div class="flex justify-between items-end mb-4">
              <div class="flex items-center gap-4">
                  <div class="flex items-center gap-6 border-b border-gray-200">
                      <button type="button" @click="tab = 'carpetas'" :class="tab === 'carpetas' ? 'text-primary border-primary' : 'text-gray-400 border-transparent hover:text-gray-600'" class="text-xl font-bold pb-2 border-b-2 transition-colors">Carpetas</button>
                      <button type="button" @click="tab = 'expedientes'" hx-get="/api/v1/agn/expedientes/explorer" hx-target="#expedientes-grid" :class="tab === 'expedientes' ? 'text-primary border-primary' : 'text-gray-400 border-transparent hover:text-gray-600'" class="text-xl font-bold pb-2 border-b-2 transition-colors">Expedientes</button>
                  </div>"""

new_tabs = """      <section class="mb-8" x-data="{ dragHover: null }">
          <div class="flex justify-between items-end mb-4">
              <div class="flex items-center gap-4">
                  <div class="flex items-center gap-6 border-b border-gray-200">
                      <h2 class="text-xl font-bold pb-2 border-b-2 border-primary text-primary">Carpetas</h2>
                  </div>"""

content = content.replace(old_tabs, new_tabs)

old_expedientes = """          <div x-show="tab === 'expedientes'" x-cloak>
              <div id="expedientes-grid" class="mb-8">
                  <!-- HTMX will load the expedientes list here -->
              </div>
          </div>"""

content = content.replace(old_expedientes, "")
content = content.replace("""<div x-show="tab === 'carpetas'">""", """<div>""")

with open("app/templates/components/explorer.html", "w", encoding="utf-8") as f:
    f.write(content)
