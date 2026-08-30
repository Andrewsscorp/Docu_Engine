with open("app/templates/pages/dashboard.html", "r", encoding="utf-8") as f:
    content = f.read()

old_section = """<!-- EXPLORER VIEW -->
<section class="min-w-0 w-full flex-1 flex flex-col" x-show="currentView === 'explorer'\""""

new_section = """<!-- EXPEDIENTE INNER VIEW -->
<section x-show="currentView === 'expediente'" class="min-w-0 w-full flex-1 flex flex-col" x-transition.opacity.duration.300ms x-cloak>
    <button @click="currentView = 'explorer'" class="mb-4 text-primary font-bold hover:underline flex items-center gap-1 w-max">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
        Volver al Explorador
    </button>
    <div id="expediente-inner-container">
        <!-- HTMX will load the Expediente SGDEA Enterprise View here -->
    </div>
</section>

<!-- EXPLORER VIEW -->
<section class="min-w-0 w-full flex-1 flex flex-col" x-show="currentView === 'explorer'\""""

if "currentView === 'expediente'" not in content:
    content = content.replace(old_section, new_section)
    with open("app/templates/pages/dashboard.html", "w", encoding="utf-8") as f:
        f.write(content)
