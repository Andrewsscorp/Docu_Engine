with open("app/templates/components/subseries_module.html", "r", encoding="utf-8") as f:
    content = f.read()

# Wrap the current content in the right pane of a 2-column layout
new_content = """<div class="flex gap-6 h-full w-full">
    <!-- TRD Tree Panel (Left) -->
    <div class="w-[300px] bg-white rounded-2xl shadow-sm border border-gray-100 p-4 shrink-0 flex flex-col h-full" hx-get="/api/v1/agn/tree_html" hx-trigger="load">
        <div class="flex flex-col items-center justify-center h-full text-gray-400 gap-3">
            <svg class="animate-spin h-8 w-8 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
            <span class="text-sm font-medium">Cargando TRD...</span>
        </div>
    </div>
    
    <!-- Main Panel (Right) -->
    <div class="flex-1 min-w-0 flex flex-col h-full overflow-hidden bg-white rounded-2xl border border-gray-100 shadow-sm">
""" + content + """
    </div>
</div>
"""

with open("app/templates/components/subseries_module.html", "w", encoding="utf-8") as f:
    f.write(new_content)
