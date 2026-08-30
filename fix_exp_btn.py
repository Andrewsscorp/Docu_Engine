with open("app/templates/pages/expediente_view.html", "r", encoding="utf-8") as f:
    content = f.read()

old_btn = 'hx-get="/api/v1/agn/subseries/{{ exp.subserie_id }}/fuid"'
new_btn = 'hx-get="/api/v1/agn/subseries/{{ exp.subserie_id }}/fuid?expediente_id={{ exp.id }}"'

content = content.replace(old_btn, new_btn)

with open("app/templates/pages/expediente_view.html", "w", encoding="utf-8") as f:
    f.write(content)
