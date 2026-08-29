with open('app/templates/components/explorer_results.html', 'r', encoding='utf-8') as f:
    content = f.read()

bad = '''@click="currentDocId = '{{ doc.id }}'; drawerAbierto = true; ('open-drawer', '{{ doc.id }}')"
                     draggable="true" 
                     @dragstart="event.dataTransfer.setData(\\'text/plain\\', \\'{{ doc.id }}\\'); event.dataTransfer.effectAllowed = \\'move\\';"'''

good = '''@click="currentDocId = '{{ doc.id }}'; drawerAbierto = true; ('open-drawer', '{{ doc.id }}')"
                     draggable="true" 
                     @dragstart="event.dataTransfer.setData('text/plain', '{{ doc.id }}'); event.dataTransfer.effectAllowed = 'move';">'''

content = content.replace(bad, good)

# Also try the raw version in case it's literally that
bad2 = '''@click="currentDocId = '{{ doc.id }}'; drawerAbierto = true; ('open-drawer', '{{ doc.id }}')"
                     draggable="true" 
                     @dragstart="event.dataTransfer.setData(\\'text/plain\\', \\'{{ doc.id }}\\'); event.dataTransfer.effectAllowed = \\'move\\';"'''
# The actual text is event.dataTransfer.setData(\'text/plain\', \'{{ doc.id }}\'); event.dataTransfer.effectAllowed = \'move\';"
import re
content = re.sub(r"draggable=\"true\"\s*@dragstart=\"[^\"]+\"", r"draggable=\"true\" @dragstart=\"event.dataTransfer.setData('text/plain', '{{ doc.id }}'); event.dataTransfer.effectAllowed = 'move';\">", content)

with open('app/templates/components/explorer_results.html', 'w', encoding='utf-8') as f:
    f.write(content)
