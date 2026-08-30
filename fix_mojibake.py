with open("app/templates/components/explorer_results.html", "r", encoding="utf-8") as f:
    content = f.read()

import re
# The mojibake is "Y\"\"" or similar depending on how python reads it. Let's just replace the whole span class
content = re.sub(r'<span class="text-3xl opacity-50">.*?</span>', '<span class="text-3xl opacity-50 font-bold text-gray-400">PDF</span>', content)

with open("app/templates/components/explorer_results.html", "w", encoding="utf-8") as f:
    f.write(content)
