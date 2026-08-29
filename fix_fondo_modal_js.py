with open('app/templates/components/explorer.html', 'r', encoding='utf-8') as f:
    content = f.read()

js_to_add = '''
          window.openCrearFondoModal = function() {
              Swal.fire({
                  width: '600px',
                  padding: 0,
                  showConfirmButton: false,
                  customClass: { popup: 'rounded-2xl overflow-hidden' },
                  didOpen: () => {
                      Swal.showLoading();
                      fetch('/api/v1/agn/modal/fondo')
                          .then(r => r.text())
                          .then(html => {
                              Swal.getPopup().innerHTML = html;
                          });
                  }
              });
          };
'''

if "window.openCrearFondoModal =" not in content:
    content = content.replace("window.openAgnModal = function() {", js_to_add + "\n          window.openAgnModal = function() {")
    with open('app/templates/components/explorer.html', 'w', encoding='utf-8') as f:
        f.write(content)
