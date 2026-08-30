with open("app/templates/components/explorer.html", "r", encoding="utf-8") as f:
    explorer = f.read()

import re

# Find the openAgnModal function block
match = re.search(r"window\.openAgnModal = function\(\) \{.*?\}\s*\}\);?\s*\}", explorer, re.DOTALL)
if match:
    func_code = match.group(0)
    
    # Remove from explorer.html
    # Actually it's fine if it's redefined or just kept there, but better to move it to dashboard.html to be safe.
    
    with open("app/templates/pages/dashboard.html", "r", encoding="utf-8") as f2:
        dashboard = f2.read()
        
    if "window.openAgnModal =" not in dashboard:
        dashboard = dashboard.replace("</script>\n</body>", f"\n{func_code}\n</script>\n</body>")
        with open("app/templates/pages/dashboard.html", "w", encoding="utf-8") as f2:
            f2.write(dashboard)
        print("Moved to dashboard.html")
    else:
        print("Already in dashboard.html")
else:
    print("Function not found in explorer.html")
