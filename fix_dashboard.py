import re

with open('app/templates/pages/dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# The original block starts with "<!-- Upload Zone -->"
# and ends with "<script>" or something? Let's check where it ends.
# I will just write a python script to find <!-- Upload Zone --> and the next <!-- ... -->
# Actually let's just find the function documentUploader() { ... } and remove it.

html = re.sub(r'<!-- Upload Zone -->.*?<div class="flex justify-between items-center mb-6">', r'''
    <!-- Upload Zone (HTMX) -->
    <div class="mb-10">
        <form 
            id="form-upload-documento"
            hx-encoding="multipart/form-data" 
            hx-post="/api/v1/documents/upload-initial" 
            hx-target="#modal-container" 
            hx-swap="innerHTML"
            class="relative border-2 border-dashed border-indigo-200 rounded-xl bg-slate-50 p-10 text-center hover:bg-indigo-50 transition-colors"
        >
            <input type="file" name="archivo" id="archivo-upload" class="hidden" accept=".pdf,.docx,.jpg,.png" 
                   onchange="document.getElementById('btn-submit-upload').click()">

            <div class="pointer-events-none">
                <div class="w-12 h-12 bg-indigo-500 rounded-full flex items-center justify-center mx-auto mb-4 text-white shadow-lg">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path></svg>
                </div>
                <h3 class="text-xl font-bold text-slate-800">Cargar Nuevos Documentos</h3>
                <p class="text-sm text-slate-500 mt-2">Arrastra y suelta tus archivos aquí, o haz clic para buscar.</p>
            </div>

            <button type="button" onclick="document.getElementById('archivo-upload').click()" class="mt-6 px-6 py-2 bg-indigo-600 text-white font-medium rounded-lg shadow-sm hover:bg-indigo-700 focus:ring-4 focus:ring-indigo-100 transition-all">
                Seleccionar archivos
            </button>

            <button type="submit" id="btn-submit-upload" class="hidden"></button>
            <progress id="upload-progress" value="0" max="100" class="htmx-indicator w-full mt-4 h-2 rounded-full overflow-hidden"></progress>
        </form>
    </div>

    <!-- Documentos Recientes -->
    <div class="flex justify-between items-center mb-6">
''', html, flags=re.DOTALL)

# Remove the JS function documentUploader
html = re.sub(r'function documentUploader\(\) \{.*?\n\s*\}\n', '', html, flags=re.DOTALL)

with open('app/templates/pages/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)
