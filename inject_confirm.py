with open("app/templates/pages/dashboard.html", "r", encoding="utf-8") as f:
    content = f.read()

global_htmx_confirm = """
    // Global HTMX Confirm to SweetAlert2
    document.body.addEventListener('htmx:confirm', function(evt) {
        evt.preventDefault();
        Swal.fire({
            title: '¿Estás seguro?',
            text: evt.detail.question,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#4f46e5',
            cancelButtonColor: '#ef4444',
            confirmButtonText: 'Sí, continuar',
            cancelButtonText: 'Cancelar',
            customClass: {
                popup: 'rounded-2xl',
                confirmButton: 'rounded-xl font-bold px-6 py-2',
                cancelButton: 'rounded-xl font-bold px-6 py-2'
            }
        }).then((result) => {
            if (result.isConfirmed) {
                evt.detail.issueRequest(true); 
            }
        });
    });
</script>
"""

content = content.replace("</script>\n</body>", global_htmx_confirm + "</body>")

with open("app/templates/pages/dashboard.html", "w", encoding="utf-8") as f:
    f.write(content)
