with open("app/templates/components/expedientes_module.html", "r", encoding="utf-8") as f:
    content = f.read()

new_js = """    function verMetadatos(id) {
        Swal.fire({
            title: 'Metadatos del Expediente',
            html: 'Cargando...',
            showConfirmButton: true,
            confirmButtonText: 'Cerrar',
            confirmButtonColor: '#4f46e5',
            didOpen: () => {
                Swal.showLoading();
                fetch(`/api/v1/agn/expedientes/${id}/metadata`)
                    .then(r => r.text())
                    .then(html => {
                        Swal.hideLoading();
                        Swal.getHtmlContainer().innerHTML = html;
                    });
            }
        });
    }

    function cerrarExpediente"""

content = content.replace("function cerrarExpediente", new_js)

# Also update the catch block of cerrarExpediente as planned earlier
old_cerrar_js = """                .then(r => r.json())
                .then(data => {
                    if(data.status === 'success') {
                        Swal.fire('Sellado!', data.detail, 'success');
                        htmx.trigger('#expedientes-filters', 'reloadExpedientes');
                    } else {
                        Swal.fire('Error', 'No se pudo sellar el expediente.', 'error');
                    }
                });"""

new_cerrar_js = """                .then(async r => {
                    const data = await r.json();
                    if(r.ok && data.status === 'success') {
                        Swal.fire('Sellado!', data.detail, 'success');
                        htmx.trigger('#expedientes-filters', 'reloadExpedientes');
                    } else {
                        Swal.fire('Operación Denegada', data.detail || 'No se pudo sellar el expediente.', 'error');
                    }
                });"""

content = content.replace(old_cerrar_js, new_cerrar_js)

with open("app/templates/components/expedientes_module.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated js for verMetadatos and error handling")
