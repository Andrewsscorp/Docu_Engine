with open("app/templates/components/explorer.html", "r", encoding="utf-8") as f:
    content = f.read()

# Inject hidden input
hidden_inputs = """
    <!-- Hidden inputs for filters -->
    <input type="hidden" name="agn_expediente_id" id="agn_expediente_id" value="">
"""

content = content.replace("<!-- Hidden inputs for filters -->", hidden_inputs)

# Update hx-include to include this new input
content = content.replace("[name='folder_filter']\"", "[name='folder_filter'], #agn_expediente_id\"")

with open("app/templates/components/explorer.html", "w", encoding="utf-8") as f:
    f.write(content)
