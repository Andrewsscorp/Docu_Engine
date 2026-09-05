with open("app/templates/components/explorer.html", "r", encoding="utf-8") as f:
    content = f.read()

# We want to wrap the entire contents of `<div x-data="{ vista: 'cuadricula'...` 
# with the two-column layout.

header = content[:content.find("<!-- Hidden inputs for filters -->")]
body = content[content.find("<!-- Hidden inputs for filters -->"):]

new_content = header + """
<div class="flex gap-6 h-full w-full">
    <!-- TRD Tree Panel (Left) -->
    <div class="w-[300px] bg-white rounded-2xl shadow-sm border border-gray-100 p-4 shrink-0 flex flex-col h-full" hx-get="/api/v1/agn/tree_html" hx-trigger="load">
        <div class="flex flex-col items-center justify-center h-full text-gray-400 gap-3">
            <svg class="animate-spin h-8 w-8 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            <span class="text-sm font-medium">Cargando TRD...</span>
        </div>
    </div>

    <!-- Main Documents Panel (Right) -->
    <div class="flex-1 min-w-0 flex flex-col h-full overflow-hidden">
""" + body + """
    </div>
</div>
"""

# Now we need to remove the closing div of the original container if it was wrapped.
# But `header` still contains `<div x-data="...">`. 
# Wait, I just injected the split INSIDE the `x-data` container. 
# So the closing div at the end of the file will close the `x-data` container, 
# but my new `<div class="flex gap-6...">` and `<div class="flex-1...">` need to be closed.

# Let's fix the closing tags.
# Replace the last `</div>` with `</div></div></div>`
new_content = new_content.rstrip()
if new_content.endswith("</div>"):
    new_content = new_content[:-6] + "</div></div></div>\n"

with open("app/templates/components/explorer.html", "w", encoding="utf-8") as f:
    f.write(new_content)
