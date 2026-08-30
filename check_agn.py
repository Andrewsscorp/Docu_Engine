with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re
matches = re.search(r"def get_fuid_subserie.*?:", content, re.DOTALL)
print(matches.group(0) if matches else "Not found")
