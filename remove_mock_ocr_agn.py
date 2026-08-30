with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re
old_str = "background_tasks.add_task(iniciar_extraccion_ocr, new_doc_id)"
new_str = "# background_tasks.add_task(iniciar_extraccion_ocr, new_doc_id) # DELEGATED TO REAL OCR WORKER"
content = content.replace(old_str, new_str)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
