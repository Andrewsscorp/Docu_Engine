with open("app/templates/pages/expediente_view.html", "r", encoding="utf-8") as f:
    content = f.read()

old_dropdown = """                      <select name="tipologia_id" required x-model="selectedTipo" class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm">
                          <option value="">-- Seleccionar Tipo --</option>
                          {% for tip in tipologias %}
                          <option value="{{ tip.id }}">{{ tip.nombre_oficial }} {% if tip.obligatoria %}(Requerido){% endif %}</option>
                          {% endfor %}
                      </select>"""

new_dropdown = """                      <select name="tipologia_id" required x-model="selectedTipo" class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm">
                          <option value="">-- Seleccionar Tipo --</option>
                          <option value="ANEXO">Archivo Adjunto / Anexo</option>
                          {% for tip in dropdown_tipologias %}
                          <option value="{{ tip.id }}">{{ tip.nombre_oficial }}</option>
                          {% endfor %}
                      </select>"""

if old_dropdown in content:
    content = content.replace(old_dropdown, new_dropdown)
else:
    print("Old dropdown not found")

with open("app/templates/pages/expediente_view.html", "w", encoding="utf-8") as f:
    f.write(content)
