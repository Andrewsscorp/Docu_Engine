import os
for root, dirs, files in os.walk("app"):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                if "FAILED" in content:
                    print(f"Found FAILED in {path}")
