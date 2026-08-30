with open("app/templates/pages/expediente_view.html", "r", encoding="utf-8") as f:
    content = f.read()

import re
old_xdata = r'x-data="\{ addDocModal: false, metadataModal: false, selectedDoc: \x27\x27, selectedTipo: \x27\x27 \}"'
new_xdata = 'x-data="{ addDocModal: false, metadataModal: false, selectedDoc: \'\', selectedTipo: \'\', visorAbierto: false, visorPdfUrl: \'\', mostrarFiltro: false, filtroDoc: \'\' }"'

content = re.sub(old_xdata, new_xdata, content)

with open("app/templates/pages/expediente_view.html", "w", encoding="utf-8") as f:
    f.write(content)
