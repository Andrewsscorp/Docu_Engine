import os
for root, dirs, files in os.walk("app/templates"):
    for file in files:
        if file.endswith(".html"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                if "Nuevo Documento" in f.read():
                    print(f"Found in {path}")
