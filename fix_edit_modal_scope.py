with open('app/templates/pages/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the Edit Modal scope issue
old_edit_modal_start = '''    <!-- El Modal de Edición de Etiquetas -->
    <div x-show="showEditModal" x-transition.opacity style="display: none;" class="fixed inset-0 z-[100] flex items-center justify-center p-4 backdrop-blur-sm bg-gray-900/50" 
         @edit-tag.window="
            showEditModal = true; 
            editTagId = .detail.id; 
            tagName = .detail.nombre; 
            currentBg = .detail.bg; 
            currentText = .detail.text; 
            tagCat = .detail.cat;
            selectedTheme = themes.find(t => t.bg === currentBg)?.id || 'indigo';
         "
         @click.self="showEditModal = false">
         
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden animate-fade-in-up" x-data="{ '''

new_edit_modal_start = '''    <!-- El Modal de Edición de Etiquetas -->
    <div x-show="showEditModal" x-transition.opacity style="display: none;" class="fixed inset-0 z-[100] flex items-center justify-center p-4 backdrop-blur-sm bg-gray-900/50" 
         @click.self="showEditModal = false">
         
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden animate-fade-in-up" 
             @edit-tag.window="
                showEditModal = true; 
                editTagId = .detail.id; 
                tagName = .detail.nombre; 
                currentBg = .detail.bg; 
                currentText = .detail.text; 
                tagCat = .detail.cat;
                selectedTheme = themes.find(t => t.bg === currentBg)?.id || 'indigo';
             "
             x-data="{ '''

content = content.replace(old_edit_modal_start, new_edit_modal_start)

with open('app/templates/pages/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed Edit Modal scope!")
