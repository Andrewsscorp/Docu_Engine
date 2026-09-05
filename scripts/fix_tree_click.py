with open("app/templates/components/agn_tree.html", "r", encoding="utf-8") as f:
    content = f.read()

# Replace the click handler for expediente
old_click = """@click=\"document.getElementById('explorer-grid').setAttribute('hx-get', '/api/v1/documents/explorer?agn_expediente_id={{ node.id }}'); htmx.process(document.getElementById('explorer-grid')); htmx.trigger('#explorer-grid', 'reloadExplorer')\""""
new_click = """@click=\"document.getElementById('agn_expediente_id').value = '{{ node.id }}'; htmx.trigger('#explorer-search-input', 'search')\""""

content = content.replace(old_click, new_click)

with open("app/templates/components/agn_tree.html", "w", encoding="utf-8") as f:
    f.write(content)
