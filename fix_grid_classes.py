with open("app/templates/components/expedientes_grid.html", "r", encoding="utf-8") as f:
    content = f.read()

import re

# Remove the static grid-cols classes
content = content.replace('class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"', 'class="grid gap-4"')

with open("app/templates/components/expedientes_grid.html", "w", encoding="utf-8") as f:
    f.write(content)
