with open('app/routers/agn.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# We want to replace the div holding the Acto Administrativo with x-data="{'fileName': ''}" and add the template below it.
# Let's locate the Acto Administrativo block accurately.

old_block = r'''<div>
                    <div class="flex items-center gap-1.5 mb-1">
                    <label class="block text-xs font-bold text-gray-600">Acto Administrativo</label>
                    <div class="relative group flex items-center">
                        <span class="flex items-center justify-center w-3 h-3 rounded-full border border-gray-400 text-gray-400 text-\[8px\] font-bold cursor-help hover:border-gray-600 hover:text-gray-600 transition-colors">\?</span>
                        <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 w-48 text-center px-2 py-1 bg-gray-800 text-white text-\[10px\] font-medium rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all shadow z-\[100\] whitespace-normal leading-tight">
                            Ley, decreto o resolución que crea formalmente la entidad.
                            <div class="absolute top-full left-1/2 -translate-x-1/2 border-\[3px\] border-transparent border-t-gray-800"></div>
                        </div>
                    </div>
                </div>
                    <div class="relative">
                        <input type="text" name="acto_administrativo" required placeholder="Resolución, Decreto, etc." class="w-full px-3 py-2 pr-10 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-colors">
                        <label class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-indigo-600 cursor-pointer">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path></svg>
                            <input type="file" name="archivo_acto" class="hidden" accept="\.pdf">
                        </label>
                    </div>
                </div>'''

new_block = '''<div x-data="{ fileName: '' }">
                    <div class="flex items-center gap-1.5 mb-1">
                    <label class="block text-xs font-bold text-gray-600">Acto Administrativo</label>
                    <div class="relative group flex items-center">
                        <span class="flex items-center justify-center w-3 h-3 rounded-full border border-gray-400 text-gray-400 text-[8px] font-bold cursor-help hover:border-gray-600 hover:text-gray-600 transition-colors">?</span>
                        <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 w-48 text-center px-2 py-1 bg-gray-800 text-white text-[10px] font-medium rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all shadow z-[100] whitespace-normal leading-tight">
                            Ley, decreto o resolución que crea formalmente la entidad.
                            <div class="absolute top-full left-1/2 -translate-x-1/2 border-[3px] border-transparent border-t-gray-800"></div>
                        </div>
                    </div>
                </div>
                    <div class="relative">
                        <input type="text" name="acto_administrativo" required placeholder="Resolución, Decreto, etc." class="w-full px-3 py-2 pr-10 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-colors">
                        <label class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-indigo-600 cursor-pointer">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path></svg>
                            <input type="file" x-ref="fileInput" name="archivo_acto" class="hidden" accept=".pdf" @change="fileName = .fileInput.files[0] ? .fileInput.files[0].name : ''">
                        </label>
                    </div>
                    
                    <template x-if="fileName">
                        <div class="mt-2 flex items-center justify-between px-3 py-1.5 bg-indigo-50 border border-indigo-100 rounded text-xs text-indigo-700 shadow-sm animate-fade-in-down">
                            <div class="flex items-center gap-2 truncate">
                                <svg class="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                                <span x-text="fileName" class="truncate font-medium"></span>
                            </div>
                            <button type="button" @click=".fileInput.value = ''; fileName = ''" class="ml-2 text-indigo-400 hover:text-red-500 focus:outline-none transition-colors">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                            </button>
                        </div>
                    </template>
                </div>'''

content = re.sub(old_block, new_block.replace("\\", ""), content) # Remove backslashes used for regex escaping

with open('app/routers/agn.py', 'w', encoding='utf-8') as f:
    f.write(content)
