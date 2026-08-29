with open('app/templates/components/explorer.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_btn = '''<button type="button" class="text-xs font-semibold text-primary hover:underline flex items-center gap-1">'''
new_btn = '''<button type="button" onclick="window.openAgnModal()" class="text-xs font-semibold text-primary hover:underline flex items-center gap-1">'''

content = content.replace(old_btn, new_btn)

# Add window.openAgnModal javascript function
js_to_add = '''
          window.openAgnModal = function() {
              Swal.fire({
                  width: '800px',
                  padding: 0,
                  showConfirmButton: false,
                  customClass: { popup: 'rounded-2xl overflow-hidden' },
                  didOpen: () => {
                      Swal.showLoading();
                      fetch('/api/v1/agn/modal')
                          .then(r => r.text())
                          .then(html => {
                              Swal.getPopup().innerHTML = html;
                          });
                  }
              });
          };

          window.submitAgnExpediente = function() {
              Swal.showLoading();
              fetch('/api/v1/agn/expedientes', { method: 'POST' })
                  .then(r => r.json())
                  .then(data => {
                      Swal.fire('Éxito', data.message, 'success');
                  });
          };
'''

content = content.replace("window.createFolder = function() {", js_to_add + "\n          window.createFolder = function() {")

with open('app/templates/components/explorer.html', 'w', encoding='utf-8') as f:
    f.write(content)
