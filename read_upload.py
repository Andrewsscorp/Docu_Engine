with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
print("--- 1439 ---")
for j in range(1439, 1450):
    print(lines[j].strip())
print("--- 2306 ---")
for j in range(2306, 2330):
    print(lines[j].strip())
