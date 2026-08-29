with open('app/routers/agn.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'require_permission("documentos:crear")',
    'require_permission("documentos:subir")'
)

with open('app/routers/agn.py', 'w', encoding='utf-8') as f:
    f.write(content)
