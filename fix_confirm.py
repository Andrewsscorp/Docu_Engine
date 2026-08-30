with open("app/templates/pages/control_tipologias.html", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    'hx-target="#expediente-inner-container"\n                                    class="p-2 text-red-300',
    'hx-target="#expediente-inner-container"\n                                    hx-confirm="¿Desvincular este requisito del expediente?"\n                                    class="p-2 text-red-300'
)

with open("app/templates/pages/control_tipologias.html", "w", encoding="utf-8") as f:
    f.write(content)
