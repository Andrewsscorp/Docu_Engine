with open("app/routers/documents.py", "r", encoding="utf-8") as f:
    content = f.read()

old_str = "background_tasks.add_task(iniciar_extraccion_ocr, documento_id)"
new_str = "# background_tasks.add_task(iniciar_extraccion_ocr, documento_id) # DELEGATED TO REAL OCR WORKER"
content = content.replace(old_str, new_str)

with open("app/routers/documents.py", "w", encoding="utf-8") as f:
    f.write(content)
