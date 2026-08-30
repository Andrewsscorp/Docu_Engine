with open("app/routers/documents.py", "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if "background_tasks.add_task(iniciar_extraccion_ocr" in line:
            print(f"Line {i}: {line.strip()}")
