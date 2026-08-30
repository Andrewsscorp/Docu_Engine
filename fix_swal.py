with open("app/templates/components/modal_vincular_trd.html", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("} catch(e) {\n                console.error(e);\n            }", "} catch(e) {\n                console.error(e);\n                Swal.fire('Error', 'Ocurrió un error inesperado al comunicarse con el servidor.', 'error');\n            }")

with open("app/templates/components/modal_vincular_trd.html", "w", encoding="utf-8") as f:
    f.write(content)
