import os
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    if "ocr" in f.read().lower():
                        print(f"Found OCR in {path}")
            except:
                pass
