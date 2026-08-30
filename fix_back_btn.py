with open("app/templates/pages/dashboard.html", "r", encoding="utf-8") as f:
    content = f.read()

import re

old_back_btn = """<!-- EXPEDIENTE INNER VIEW -->
<section x-show="currentView === 'expediente'" class="min-w-0 w-full flex-1 flex flex-col" x-transition.opacity.duration.300ms x-cloak>
    <button @click="currentView = 'explorer'" class="mb-4 text-primary font-bold hover:underline flex items-center gap-1 w-max">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
        Volver al Explorador
    </button>"""

new_back_btn = """<!-- EXPEDIENTE INNER VIEW -->
<section x-show="currentView === 'expediente'" class="min-w-0 w-full flex-1 flex flex-col" x-transition.opacity.duration.300ms x-cloak>
    <button @click="currentView = 'expedientes_module'" class="mb-4 text-primary font-bold hover:underline flex items-center gap-1 w-max transition-transform hover:-translate-x-1">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
        Volver a Expedientes
    </button>"""

content = content.replace(old_back_btn, new_back_btn)

with open("app/templates/pages/dashboard.html", "w", encoding="utf-8") as f:
    f.write(content)
