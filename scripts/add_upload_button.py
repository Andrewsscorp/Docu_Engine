with open("app/templates/components/explorer.html", "r", encoding="utf-8") as f:
    content = f.read()

upload_form = """
          <!-- UPLOAD TRD FORM -->
          <form id="form-upload-trd" hx-encoding="multipart/form-data" hx-post="/api/v1/documents/upload-initial" hx-trigger="submit" hx-target="#modal-container" hx-swap="innerHTML" class="hidden">
              <input type="file" name="archivo" id="archivo-upload-trd" accept=".pdf,.docx,.jpg,.png" onchange="htmx.trigger('#form-upload-trd', 'submit')">
              <input type="hidden" name="agn_expediente_id" id="upload_agn_expediente_id" value="">
          </form>

          <button onclick="let exp = document.getElementById('agn_expediente_id').value; if(!exp) { Swal.fire('Error', 'Selecciona un Expediente en el arbol de la izquierda primero.', 'warning'); return; } document.getElementById('upload_agn_expediente_id').value = exp; document.getElementById('archivo-upload-trd').click();" class="ml-2 flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-sm py-2 px-4 rounded-lg transition-colors shadow-sm">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path></svg>
            Subir Documento
          </button>
"""

import re
# Insert the upload form before the "Nueva Carpeta" button
content = re.sub(r'(<button @click="createFolder\(\)".*?>.*?Nueva Carpeta\s*</button>)', upload_form + r'\1', content, flags=re.DOTALL)

with open("app/templates/components/explorer.html", "w", encoding="utf-8") as f:
    f.write(content)
