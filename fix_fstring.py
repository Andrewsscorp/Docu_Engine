with open('app/routers/agn.py', 'r', encoding='utf-8') as f:
    content = f.read()

# I will find the script block and replace { and } with {{ and }}
import re

# We know the error is at: if(evt.detail.elt.id === 'crear-fondo-form') {
# Let's just fix the whole script block.
# Actually, since it's just Python string manipulation, I'll replace the problematic parts manually.

old_script = '''    <script>
        htmx.process(document.getElementById('crear-fondo-form'));
        
        document.body.addEventListener('htmx:responseError', function(evt) {
            if(evt.detail.elt.id === 'crear-fondo-form') {
                try {
                    const resp = JSON.parse(evt.detail.xhr.response);
                    Swal.fire('Error', resp.detail, 'error');
                } catch(e) {
                    Swal.fire('Error', 'Ocurrió un error en el servidor.', 'error');
                }
            }
        });
        document.body.addEventListener('htmx:afterRequest', function(evt) {
            if(evt.detail.elt.id === 'crear-fondo-form' && evt.detail.successful) {
                Swal.fire({
                    title: '¡Fondo Creado!',
                    text: 'El fondo documental ha sido registrado exitosamente.',
                    icon: 'success',
                    timer: 1500,
                    showConfirmButton: false
                }).then(() => {
                    // Reopen the main AGN modal
                    window.openAgnModal();
                });
            }
        });
    </script>'''

new_script = '''    <script>
        htmx.process(document.getElementById('crear-fondo-form'));
        
        document.body.addEventListener('htmx:responseError', function(evt) {{
            if(evt.detail.elt.id === 'crear-fondo-form') {{
                try {{
                    const resp = JSON.parse(evt.detail.xhr.response);
                    Swal.fire('Error', resp.detail, 'error');
                }} catch(e) {{
                    Swal.fire('Error', 'Ocurrió un error en el servidor.', 'error');
                }}
            }}
        }});
        document.body.addEventListener('htmx:afterRequest', function(evt) {{
            if(evt.detail.elt.id === 'crear-fondo-form' && evt.detail.successful) {{
                Swal.fire({{
                    title: '¡Fondo Creado!',
                    text: 'El fondo documental ha sido registrado exitosamente.',
                    icon: 'success',
                    timer: 1500,
                    showConfirmButton: false
                }}).then(() => {{
                    // Reopen the main AGN modal
                    window.openAgnModal();
                }});
            }}
        }});
    </script>'''

content = content.replace(old_script, new_script)

with open('app/routers/agn.py', 'w', encoding='utf-8') as f:
    f.write(content)
