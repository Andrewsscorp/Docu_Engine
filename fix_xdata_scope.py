with open("app/templates/components/expedientes_module.html", "r", encoding="utf-8") as f:
    content = f.read()

import re

# Move x-data to the top-level container instead of just the header
content = content.replace('<div class="px-8 pt-8 pb-6 bg-white border-b border-gray-100 flex flex-col gap-6" x-data="{ viewMode: \'grid\' }">',
                          '<div class="px-8 pt-8 pb-6 bg-white border-b border-gray-100 flex flex-col gap-6">')

# We need a top level wrapper for the whole module
content = f"""<div class="flex flex-col h-full w-full" x-data="{{ viewMode: 'grid' }}">
{content}
</div>"""

with open("app/templates/components/expedientes_module.html", "w", encoding="utf-8") as f:
    f.write(content)
