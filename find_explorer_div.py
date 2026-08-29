import re

with open('app/templates/pages/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's see how explorer is loaded
match = re.search(r'<div[^>]*hx-get="/api/v1/documents/explorer"[^>]*>', content)
if match:
    print("Found:", match.group(0))
else:
    print("Not found")
