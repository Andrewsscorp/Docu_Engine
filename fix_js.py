with open("app/templates/components/expedientes_module.html", "r", encoding="utf-8") as f:
    content = f.read()

import re

old_script = re.search(r'<script>\s*function editExpediente.*?</script>', content, re.DOTALL)
if not old_script:
    print("Script not found!")
    exit(1)

new_script = """<script>
    function editExpediente(id, nombre, soporteActual) {
        Swal.fire({
            title: 'Editar Expediente',
            html: `
                <div class="space-y-4 text-left">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Título del Expediente</label>
                        <input id="swal-input-nombre" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-primary" value="${nombre}">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Soporte</label>
                        <select id="swal-input-soporte" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-primary">
                            <option value="ELECTRÓNICO" ${soporteActual === 'ELECTRÓNICO' ? 'selected' : ''}>Electrónico</option>
                            <option value="FÍSICO" ${soporteActual === 'FÍSICO' ? 'selected' : ''}>Físico</option>
                            <option value="HÍBRIDO" ${soporteActual === 'HÍBRIDO' ? 'selected' : ''}>Híbrido</option>
                        </select>
                    </div>
                    <p class="text-xs text-gray-500">*Para cambiar el responsable, utilice la opción de reasignación masiva o delegación.</p>
                </div>
            `,
            showCancelButton: true,
            confirmButtonText: 'Guardar',
            cancelButtonText: 'Cancelar',
            showLoaderOnConfirm: true,
            preConfirm: () => {
                const newNombre = document.getElementById('swal-input-nombre').value;
                const newSoporte = document.getElementById('swal-input-soporte').value;
                const formData = new FormData();
                formData.append('nombre_expediente', newNombre);
                formData.append('soporte', newSoporte);
                
                return fetch(`/api/v1/agn/expedientes/${id}`, {
                    method: 'PUT',
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(data => { throw new Error(data.error || 'Error desconocido') })
                    }
                    return response.json()
                })
                .catch(error => {
                    Swal.showValidationMessage(`Error: ${error.message}`)
                })
            },
            allowOutsideClick: () => !Swal.isLoading()
        }).then((result) => {
            if (result.isConfirmed) {
                Swal.fire('Guardado!', '', 'success');
                htmx.trigger('#expedientes-filters', 'reloadExpedientes');
            }
        });
    }

    function cerrarExpediente(id) {
        Swal.fire({
            title: 'Sellar Expediente',
            text: "Esta acción marcará el expediente como CERRADO, inyectará la huella criptográfica, bloqueará el ingreso de folios e iniciará la cuenta regresiva de retención según la TRD. ¡Esta acción activa la inmutabilidad de la Ley 527 y NO se puede deshacer!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc2626',
            cancelButtonColor: '#6b7280',
            confirmButtonText: 'Sellar Definitivamente'
        }).then((result) => {
            if (result.isConfirmed) {
                fetch(`/api/v1/agn/expedientes/${id}/cierre`, {
                    method: 'POST'
                })
                .then(r => r.json())
                .then(data => {
                    if(data.status === 'success') {
                        Swal.fire('Sellado!', data.detail, 'success');
                        htmx.trigger('#expedientes-filters', 'reloadExpedientes');
                    } else {
                        Swal.fire('Error', 'No se pudo sellar el expediente.', 'error');
                    }
                });
            }
        });
    }
</script>"""

content = content.replace(old_script.group(0), new_script)

with open("app/templates/components/expedientes_module.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated javascript in expedientes_module.html")
