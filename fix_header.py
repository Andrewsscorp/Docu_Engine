with open("app/templates/pages/dashboard.html", "r", encoding="utf-8") as f:
    content = f.read()

old_header = "currentView === 'tags' ? 'Gesti\u00f3n de Etiquetas' : 'Panel de Ajustes'"
new_header = "currentView === 'tags' ? 'Gesti\u00f3n de Etiquetas' : (currentView === 'expediente' ? 'Expediente Electrónico' : 'Panel de Ajustes')"

# Note: The actual file might have 'Gestin' due to encoding. Let's use regex.
import re
content = re.sub(r"currentView === 'tags' \? '([^']+)' : 'Panel de Ajustes'", r"currentView === 'tags' ? '\1' : (currentView === 'expediente' ? 'Expediente Electrónico' : 'Panel de Ajustes')", content)

with open("app/templates/pages/dashboard.html", "w", encoding="utf-8") as f:
    f.write(content)
