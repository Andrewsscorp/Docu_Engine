with open("app/templates/components/explorer.html", "r", encoding="utf-8") as f:
    content = f.read()

import re
# Remove the tree panel
content = re.sub(r'<!-- TRD Tree Panel \(Left\) -->.*?<!-- Main Documents Panel \(Right\) -->', '<!-- Main Documents Panel (Right) -->', content, flags=re.DOTALL)

# Adjust the flex gap since there is no sidebar anymore
content = content.replace('<div class="flex gap-6 h-full w-full">', '<div class="h-full w-full">')

with open("app/templates/components/explorer.html", "w", encoding="utf-8") as f:
    f.write(content)
