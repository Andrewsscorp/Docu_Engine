with open("app/templates/components/expedientes_module.html", "r", encoding="utf-8") as f:
    content = f.read()

import re

# Add h-[42px] or similar to inputs to ensure uniform height
content = content.replace('class="w-full pl-10 pr-4 py-2.5 bg-white border border-gray-200 rounded-xl focus:ring-primary focus:border-primary text-sm shadow-sm transition-all outline-none"',
                          'class="w-full h-[42px] pl-10 pr-4 bg-white border border-gray-200 rounded-xl focus:ring-primary focus:border-primary text-sm shadow-sm transition-all outline-none"')

content = content.replace('class="bg-white border border-gray-200 text-gray-700 text-sm font-medium rounded-xl focus:ring-primary focus:border-primary block p-2.5 shadow-sm min-w-[140px] outline-none"',
                          'class="h-[42px] bg-white border border-gray-200 text-gray-700 text-sm font-medium rounded-xl focus:ring-primary focus:border-primary block px-3 shadow-sm min-w-[140px] outline-none"')

content = content.replace('class="bg-white border border-gray-200 text-gray-700 text-sm font-medium rounded-xl focus:ring-primary focus:border-primary block p-2.5 shadow-sm min-w-[160px] max-w-[200px] outline-none truncate" title="Filtrar por Subserie"',
                          'class="h-[42px] bg-white border border-gray-200 text-gray-700 text-sm font-medium rounded-xl focus:ring-primary focus:border-primary block px-3 shadow-sm min-w-[180px] max-w-[240px] outline-none truncate" title="Filtrar por Subserie"')

content = content.replace('class="flex items-center gap-2 bg-white border border-gray-200 rounded-xl p-1 shadow-sm"',
                          'class="flex items-center gap-2 bg-white border border-gray-200 rounded-xl px-2 h-[42px] shadow-sm"')

content = content.replace('class="flex items-center bg-gray-100 p-1 rounded-xl border border-gray-200 ml-auto"',
                          'class="flex items-center bg-gray-100 p-1 rounded-xl border border-gray-200 ml-auto h-[42px]"')

with open("app/templates/components/expedientes_module.html", "w", encoding="utf-8") as f:
    f.write(content)
