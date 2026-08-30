with open("app/templates/pages/control_tipologias.html", "r", encoding="utf-8") as f:
    content = f.read()

import re

# Update Parametrizar TRD button
content = content.replace('hx-get="/api/v1/agn/subseries/{{ exp.subserie_id }}/modal_trd"', 'hx-get="/api/v1/agn/expedientes/{{ exp.id }}/modal_trd"')

with open("app/templates/pages/control_tipologias.html", "w", encoding="utf-8") as f:
    f.write(content)

# Update modal_vincular_trd.html
with open("app/templates/components/modal_vincular_trd.html", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('subserie.nombre', 'expediente.nombre_expediente')
content = content.replace('subserie.id', 'expediente.id')
content = content.replace('/api/v1/agn/subseries/{{ subserie.id }}/tipologias/disponibles', '/api/v1/agn/expedientes/{{ expediente.id }}/tipologias/disponibles')
content = content.replace("url: '/api/v1/agn/subseries/{{ subserie.id }}/tipologias',", "url: '/api/v1/agn/expedientes/{{ expediente.id }}/tipologias',")

with open("app/templates/components/modal_vincular_trd.html", "w", encoding="utf-8") as f:
    f.write(content)
