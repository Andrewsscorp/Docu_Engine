with open("app/templates/pages/control_tipologias.html", "r", encoding="utf-8") as f:
    lines = f.readlines()
print("--- AROUND LINE 69 ---")
for j in range(67, 85):
    print(f"{j}: {lines[j].strip()}")
print("--- AROUND LINE 94 ---")
for j in range(90, 100):
    print(f"{j}: {lines[j].strip()}")
