with open('app/routers/agn.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('.fileInput.files', '$refs.fileInput.files')
content = content.replace('.fileInput.value', '$refs.fileInput.value')

with open('app/routers/agn.py', 'w', encoding='utf-8') as f:
    f.write(content)
