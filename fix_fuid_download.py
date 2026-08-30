with open("app/templates/pages/fuid_view.html", "r", encoding="utf-8") as f:
    content = f.read()

old_script = """Swal.fire('¡Transferencia Completada!', 'El FUID fue firmado y cerrado criptográficamente.\\nHash: ' + data.hash, 'success').then(() => {
                                    window.location.reload();
                                });"""

new_script = """Swal.fire('¡Transferencia Completada!', 'El FUID fue firmado y cerrado criptográficamente.\\nHash: ' + data.hash, 'success').then(() => {
                                    window.open('/api/v1/agn/fuid/descargar_pdf/' + data.hash, '_blank');
                                    setTimeout(() => window.location.reload(), 1000);
                                });"""

content = content.replace(old_script, new_script)

with open("app/templates/pages/fuid_view.html", "w", encoding="utf-8") as f:
    f.write(content)
