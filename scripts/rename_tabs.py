import re

with open("app/templates/pages/dashboard.html", "r", encoding="utf-8") as f:
    content = f.read()

# Current Explorer Li:
# <li @click="currentView = 'explorer'" title="Documentos"
# <span x-show="sidebarOpen" x-transition.opacity>Documentos</span>

# Current Expedientes Li:
# <li @click="currentView = 'expedientes_module'" title="Expedientes"
# <span x-show="sidebarOpen" x-transition.opacity>Expedientes</span>

# We want:
# Explorer -> "Expedientes TRD"
# Expedientes -> "Configuración TRD" (or "Cuadro TRD")

content = content.replace(
    '''<li @click="currentView = 'explorer'" title="Documentos"''',
    '''<li @click="currentView = 'explorer'" title="Expedientes TRD"'''
)
content = content.replace(
    '''<span x-show="sidebarOpen" x-transition.opacity>Documentos</span>''',
    '''<span x-show="sidebarOpen" x-transition.opacity>Expedientes TRD</span>'''
)

content = content.replace(
    '''<li @click="currentView = 'expedientes_module'" title="Expedientes"''',
    '''<li @click="currentView = 'expedientes_module'" title="Cuadro TRD"'''
)
content = content.replace(
    '''<span x-show="sidebarOpen" x-transition.opacity>Expedientes</span>''',
    '''<span x-show="sidebarOpen" x-transition.opacity>Cuadro TRD</span>'''
)

# And in the header:
# (currentView === 'explorer' ? 'Documentos' : 
content = content.replace(
    "(currentView === 'explorer' ? 'Documentos' :",
    "(currentView === 'explorer' ? 'Explorador de Expedientes' :"
)

# (currentView === 'expedientes_module' ? 'Expedientes SGDEA' :
content = content.replace(
    "(currentView === 'expedientes_module' ? 'Expedientes SGDEA' :",
    "(currentView === 'expedientes_module' ? 'Cuadro de Clasificación (TRD)' :"
)

with open("app/templates/pages/dashboard.html", "w", encoding="utf-8") as f:
    f.write(content)
