with open("app/templates/pages/control_tipologias.html", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('onclick="Swal.showLoading()"', '')

# add a small script to close any swal if it was open
script = """
    <script>
        if(Swal.isVisible()) {
            Swal.close();
        }
    </script>
"""
if script not in content:
    content = content + script

with open("app/templates/pages/control_tipologias.html", "w", encoding="utf-8") as f:
    f.write(content)
