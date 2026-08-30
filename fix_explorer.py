with open("app/templates/components/explorer.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skip_mode = False

for line in lines:
    if "tab = 'carpetas'" in line and "x-data" in line:
        line = line.replace(", tab: 'carpetas'", "")
    
    if "button type=\"button\" @click=\"tab = 'carpetas'\"" in line:
        line = '                    <h2 class="text-xl font-bold pb-2 border-b-2 border-primary text-primary">Carpetas</h2>\n'
    
    if "button type=\"button\" @click=\"tab = 'expedientes'\"" in line:
        continue # Skip this line
        
    if "<div x-show=\"tab === 'carpetas'\">" in line:
        line = '        <div>\n'
        
    if "<div x-show=\"tab === 'expedientes'\" x-cloak>" in line:
        skip_mode = True
        continue
        
    if skip_mode:
        if "</div>" in line and "<!-- HTMX will load the expedientes list here -->" not in line and "id=\"expedientes-grid\"" not in line:
            # Check if this is the closing div of the expedientes tab
            # Wait, there are nested divs. Let's just be careful.
            pass
            
    if not skip_mode:
        new_lines.append(line)

with open("app/templates/components/explorer.html", "w", encoding="utf-8") as f:
    f.writelines(new_lines)
