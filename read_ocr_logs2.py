with open("ocr_logs.txt", "rb") as f:
    content = f.read().decode("utf-16", errors="ignore")

for line in content.split("\n"):
    if "Error procesando" in line:
        print(line.strip())
