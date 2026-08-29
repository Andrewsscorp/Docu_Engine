with open('app/templates/components/explorer_results.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('draggable=\\"true\\" @dragstart=\\"', 'draggable="true" @dragstart="')

with open('app/templates/components/explorer_results.html', 'w', encoding='utf-8') as f:
    f.write(content)
