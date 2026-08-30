with open("app/templates/pages/dashboard.html", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i in range(1150, 1165):
    print(f"Line {i}: {lines[i].rstrip()}")
