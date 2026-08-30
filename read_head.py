with open("app/templates/pages/control_tipologias.html", "r", encoding="utf-8") as f:
    lines = f.readlines()[:25]
with open("head_out.txt", "w", encoding="utf-8") as out:
    for line in lines:
        out.write(line)
