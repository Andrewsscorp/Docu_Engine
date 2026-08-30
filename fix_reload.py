with open("app/templates/pages/control_tipologias.html", "r", encoding="utf-8") as f:
    content = f.read()

# Add hx-trigger listener to the main div
content = content.replace('<div class="h-full flex flex-col bg-slate-50 animate-fade-in-up"',
                          '<div class="h-full flex flex-col bg-slate-50 animate-fade-in-up" hx-get="/api/v1/agn/expedientes/{{ exp.id }}/control_tipologias" hx-trigger="reloadControlTipologias from:body" hx-target="#expediente-inner-container"')

with open("app/templates/pages/control_tipologias.html", "w", encoding="utf-8") as f:
    f.write(content)

with open("app/templates/components/modal_vincular_trd.html", "r", encoding="utf-8") as f:
    content2 = f.read()

content2 = content2.replace("htmx.trigger('body', 'reloadSubseries');", "htmx.trigger('body', 'reloadControlTipologias');")

with open("app/templates/components/modal_vincular_trd.html", "w", encoding="utf-8") as f:
    f.write(content2)
