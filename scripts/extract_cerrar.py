with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    agn = f.read()

import re
match = re.search(r'(async def cerrar_expediente\(.*?return \{"status": "success".*?\}\n)', agn, re.DOTALL)
if match:
    print(match.group(1)[:500])
    print("... truncated ...")
    print(match.group(1)[-500:])
