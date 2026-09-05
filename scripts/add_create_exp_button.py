with open("app/templates/components/explorer.html", "r", encoding="utf-8") as f:
    content = f.read()

create_exp_btn = """
          <button onclick="window.openAgnModal()" class="ml-2 flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white font-medium text-sm py-2 px-4 rounded-lg transition-colors shadow-sm">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
            Nuevo Expediente TRD
          </button>
"""

import re
content = re.sub(r'(<button @click="createFolder\(\)".*?>.*?Nueva Carpeta\s*</button>)', create_exp_btn + r'\1', content, flags=re.DOTALL)

with open("app/templates/components/explorer.html", "w", encoding="utf-8") as f:
    f.write(content)
