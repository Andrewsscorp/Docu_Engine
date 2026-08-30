with open("ocr_logs.txt", "r", encoding="utf-8") as f:
    for line in f:
        if "Error" in line or "FAILED" in line or "0f00adc1" in line:
            print(line.strip())
