with open("app/templates/pages/dashboard.html", "r", encoding="utf-8") as f:
    content = f.read()

old_drop = """@drop.prevent="isDropping = false; document.getElementById('archivo-upload').files = $event.dataTransfer.files; htmx.trigger('#form-upload-documento', 'submit')" """

new_drop = """@drop.prevent="
    isDropping = false; 
    if ($event.dataTransfer.files.length > 1) { 
        Swal.fire('Atenci\u00f3n', 'Solo puedes procesar un documento a la vez.', 'warning'); 
        return; 
    } 
    document.getElementById('archivo-upload').files = $event.dataTransfer.files; 
    htmx.trigger('#form-upload-documento', 'submit');
" """

content = content.replace(old_drop, new_drop.replace('\n', ' '))

with open("app/templates/pages/dashboard.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Added single file restriction to dropzone")
