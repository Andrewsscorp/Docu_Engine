with open('app/routers/agn.py', 'r', encoding='utf-8') as f:
    content = f.read()
import re

content = re.sub(r'<label class="block text-xs font-bold text-gray-600 mb-1">C.digo Oficial del Fondo</label>', 
    '''<div class="flex items-center gap-1.5 mb-1">
                    <label class="block text-xs font-bold text-gray-600">Código Oficial del Fondo</label>
                    <div class="relative group flex items-center">
                        <span class="flex items-center justify-center w-3 h-3 rounded-full border border-gray-400 text-gray-400 text-[8px] font-bold cursor-help hover:border-gray-600 hover:text-gray-600 transition-colors">?</span>
                        <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 w-48 text-center px-2 py-1 bg-gray-800 text-white text-[10px] font-medium rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all shadow z-[100] whitespace-normal leading-tight">
                            Identificador alfanumérico único e irrepetible asignado a la entidad.
                            <div class="absolute top-full left-1/2 -translate-x-1/2 border-[3px] border-transparent border-t-gray-800"></div>
                        </div>
                    </div>
                </div>''', content)

content = re.sub(r'<label class="block text-xs font-bold text-gray-600 mb-1">Nombre de la Entidad Productora</label>', 
    '''<div class="flex items-center gap-1.5 mb-1">
                    <label class="block text-xs font-bold text-gray-600">Nombre de la Entidad Productora</label>
                    <div class="relative group flex items-center">
                        <span class="flex items-center justify-center w-3 h-3 rounded-full border border-gray-400 text-gray-400 text-[8px] font-bold cursor-help hover:border-gray-600 hover:text-gray-600 transition-colors">?</span>
                        <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 w-48 text-center px-2 py-1 bg-gray-800 text-white text-[10px] font-medium rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all shadow z-[100] whitespace-normal leading-tight">
                            Razón social legal y completa de la institución productora.
                            <div class="absolute top-full left-1/2 -translate-x-1/2 border-[3px] border-transparent border-t-gray-800"></div>
                        </div>
                    </div>
                </div>''', content)

content = re.sub(r'<label class="block text-xs font-bold text-gray-600 mb-1">Acto Administrativo</label>', 
    '''<div class="flex items-center gap-1.5 mb-1">
                    <label class="block text-xs font-bold text-gray-600">Acto Administrativo</label>
                    <div class="relative group flex items-center">
                        <span class="flex items-center justify-center w-3 h-3 rounded-full border border-gray-400 text-gray-400 text-[8px] font-bold cursor-help hover:border-gray-600 hover:text-gray-600 transition-colors">?</span>
                        <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 w-48 text-center px-2 py-1 bg-gray-800 text-white text-[10px] font-medium rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all shadow z-[100] whitespace-normal leading-tight">
                            Ley, decreto o resolución que crea formalmente la entidad.
                            <div class="absolute top-full left-1/2 -translate-x-1/2 border-[3px] border-transparent border-t-gray-800"></div>
                        </div>
                    </div>
                </div>''', content)

content = re.sub(r'<label class="block text-xs font-bold text-gray-600 mb-1">Estado del Fondo</label>', 
    '''<div class="flex items-center gap-1.5 mb-1">
                    <label class="block text-xs font-bold text-gray-600">Estado del Fondo</label>
                    <div class="relative group flex items-center">
                        <span class="flex items-center justify-center w-3 h-3 rounded-full border border-gray-400 text-gray-400 text-[8px] font-bold cursor-help hover:border-gray-600 hover:text-gray-600 transition-colors">?</span>
                        <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 w-48 text-center px-2 py-1 bg-gray-800 text-white text-[10px] font-medium rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all shadow z-[100] whitespace-normal leading-tight">
                            Condición activa o liquidada para habilitar o restringir expedientes.
                            <div class="absolute top-full left-1/2 -translate-x-1/2 border-[3px] border-transparent border-t-gray-800"></div>
                        </div>
                    </div>
                </div>''', content)

# General encoding fixes in case anything is messed up
content = re.sub(r'C.digo', 'Código', content)

with open('app/routers/agn.py', 'w', encoding='utf-8') as f:
    f.write(content)
