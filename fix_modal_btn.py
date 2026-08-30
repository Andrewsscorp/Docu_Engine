for filename in ["app/templates/components/expedientes_module.html", "app/templates/components/subseries_module.html"]:
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace('onclick="window.openAgnModal()"', 'onclick="window.openAgnModal(\'{{ subserie_id if subserie_id else \'\' }}\')"')
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
print("Updated openAgnModal calls")
