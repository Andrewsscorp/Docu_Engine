import re
with open('app/templates/pages/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()
if "hx-trigger=\"reloadExplorer from:body" in content:
    print("Found hx-trigger")
else:
    print("Not found")
