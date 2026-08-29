with open("app/templates/components/explorer.html", "r", encoding="utf-8") as f:
    content = f.read()

new_js = """
            window.openCrearSerieModal = function() {
                const fondoSelect = document.getElementById('fondo_select');
                const fondoId = fondoSelect ? fondoSelect.value : null;
                const seccionSelect = document.getElementById('seccion_select');
                const seccionId = seccionSelect ? seccionSelect.value : null;
                const subseccionSelect = document.getElementById('subseccion_select');
                const subseccionId = subseccionSelect ? subseccionSelect.value : '';
                
                if (!fondoId || !seccionId) {
                    Swal.fire('Atención', 'Debe seleccionar obligatoriamente un Fondo y una Sección Padre primero.', 'warning');
                    return;
                }
                
                Swal.fire({
                    width: '800px',
                    padding: 0,
                    showConfirmButton: false,
                    customClass: { popup: 'rounded-2xl' },
                    didOpen: () => {
                        Swal.showLoading();
                        fetch(`/api/v1/agn/modal/serie?fondo_id=${fondoId}&seccion_id=${seccionId}&subseccion_id=${subseccionId}`)
                            .then(r => r.text())
                            .then(html => {
                                Swal.getPopup().innerHTML = html;
                                if (window.htmx) { htmx.process(Swal.getPopup()); }
                                if (window.Alpine) { Alpine.initTree(Swal.getPopup()); }
                            });
                    }
                });
            };
"""

content = content.replace("window.openCrearSubseccionModal = function() {", new_js + "\n            window.openCrearSubseccionModal = function() {")

with open("app/templates/components/explorer.html", "w", encoding="utf-8") as f:
    f.write(content)
