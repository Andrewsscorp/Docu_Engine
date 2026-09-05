with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if "\"eid\": exp_id" in line:
        lines[i] = line.replace("\"eid\": exp_id", "\"sid\": subserie_id")
with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.writelines(lines)
