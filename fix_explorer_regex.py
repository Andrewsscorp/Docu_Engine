with open("app/templates/components/explorer.html", "r", encoding="utf-8") as f:
    content = f.read()

import re
content = re.sub(r"x-data=\"\{ dragHover: null, tab: 'carpetas' \}\"", r'x-data="{ dragHover: null }"', content)

content = re.sub(r"<button type=\"button\" @click=\"tab = 'carpetas'\".*?</button>", r'<h2 class="text-xl font-bold pb-2 border-b-2 border-primary text-primary">Carpetas</h2>', content, flags=re.DOTALL)

content = re.sub(r"<button type=\"button\" @click=\"tab = 'expedientes'\".*?</button>", r'', content, flags=re.DOTALL)

content = re.sub(r"<div x-show=\"tab === 'expedientes'\" x-cloak>\s*<div id=\"expedientes-grid\" class=\"mb-8\">\s*<!-- HTMX will load the expedientes list here -->\s*</div>\s*</div>", r'', content, flags=re.DOTALL)

with open("app/templates/components/explorer.html", "w", encoding="utf-8") as f:
    f.write(content)
