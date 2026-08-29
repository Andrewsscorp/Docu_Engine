with open('app/routers/agn.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('Clasificacin', 'Clasificación')
content = content.replace('ELECTRNICO', 'ELECTRÓNICO')
content = content.replace('Seccin', 'Sección')
content = content.replace('Subseccin', 'Subsección')
content = content.replace('Automticamente', 'Automáticamente')
content = content.replace('Inmutable', 'Inmutable')
content = content.replace('Identificacin', 'Identificación')
content = content.replace('Prestacin', 'Prestación')
content = content.replace('Alcalda', 'Alcaldía')
content = content.replace('Secretara', 'Secretaría')
content = content.replace('Educacin', 'Educación')
content = content.replace('Asunto', 'Asunto') # Just in case

# Actually I can just write a script that does global replacements for all the broken ones:
fixes = {
    '': 'ó', # Let's just fix the specific words
    'Clasificacin': 'Clasificación',
    'ELECTRNICO': 'ELECTRÓNICO',
    'Seccin': 'Sección',
    'Subseccin': 'Subsección',
    'Automticamente': 'Automáticamente',
    'Identificacin': 'Identificación',
}
for k, v in fixes.items():
    content = content.replace(k, v)

with open('app/routers/agn.py', 'w', encoding='utf-8') as f:
    f.write(content)
