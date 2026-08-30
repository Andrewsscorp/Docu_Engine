with open("app/templates/components/explorer.html", "r", encoding="utf-8") as f:
    content = f.read()

import re
content = re.sub(r'<span class="text-3xl opacity-50">.*?</span>', '<span class="text-3xl opacity-50 font-bold text-gray-400">PDF</span>', content)

with open("app/templates/components/explorer.html", "w", encoding="utf-8") as f:
    f.write(content)
