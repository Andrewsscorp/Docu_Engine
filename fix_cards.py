import re

with open('app/templates/components/explorer_results.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the specific malformed block
bad_block = """                 @click="currentDocId = '{{ doc.id }}'; drawerAbierto = true; ('open-drawer', '{{ doc.id }}')">
                     draggable="true" 
                     @dragstart="event.dataTransfer.setData(\\'text/plain\\', \\'{{ doc.id }}\\'); event.dataTransfer.effectAllowed = \\'move\\';"
                 """
good_block = """                 @click="currentDocId = '{{ doc.id }}'; drawerAbierto = true; ('open-drawer', '{{ doc.id }}')"
                 draggable="true" 
                 @dragstart="event.dataTransfer.setData('text/plain', '{{ doc.id }}'); event.dataTransfer.effectAllowed = 'move';">
                 """

content = content.replace(bad_block, good_block)
# Also try without escaped slashes if they were literal
bad_block2 = """                 @click="currentDocId = '{{ doc.id }}'; drawerAbierto = true; ('open-drawer', '{{ doc.id }}')">
                     draggable="true" 
                     @dragstart="event.dataTransfer.setData(\'text/plain\', \'{{ doc.id }}\'); event.dataTransfer.effectAllowed = \'move\';"
                 """
content = content.replace(bad_block2, good_block)

# Sometimes it's easier to just find the > and move it.
pattern = r'(@click="currentDocId = \'\{\{ doc\.id \}\}\'; drawerAbierto = true; \\(\'open-drawer\', \'\{\{ doc\.id \}\}\'\)")>\s*draggable="true"\s*@dragstart="([^"]+)"'
content = re.sub(pattern, r'\1 draggable="true" @dragstart="\2">', content)

with open('app/templates/components/explorer_results.html', 'w', encoding='utf-8') as f:
    f.write(content)
