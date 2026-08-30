with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re
old_agn = 'file_path = os.path.join(upload_dir, disk_filename).replace("/", "/")'
# Wait, I previously changed it to .replace("\\\\", "/")
# Let's just do a regex replace for the INSERT query parameters

pattern_agn = r'("p": )file_path(,\s*"u": session_data\["user_id"\])'
content = re.sub(pattern_agn, r'\1disk_filename\2', content)
with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
print("agn.py updated")
