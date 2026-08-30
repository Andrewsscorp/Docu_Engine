with open("app/templates/pages/dashboard.html", "r", encoding="utf-8") as f:
    content = f.read()

import re
old_func = """window.openAgnModal = function() {
              Swal.fire({
                  width: '800px',
                  padding: 0,
                  showConfirmButton: false,
                  customClass: { popup: 'rounded-2xl' },
                  didOpen: () => {
                      Swal.showLoading();
                      fetch('/api/v1/agn/modal')
                          .then(r => r.text())
                          .then(html => {
                              Swal.getPopup().innerHTML = html;
                                if (window.htmx) { htmx.process(Swal.getPopup()); }
                                if (window.Alpine) { Alpine.initTree(Swal.getPopup()); }
                          });
                  }
</script>"""

new_func = """window.openAgnModal = function() {
    Swal.fire({
        width: '800px',
        padding: 0,
        showConfirmButton: false,
        customClass: { popup: 'rounded-2xl' },
        didOpen: () => {
            Swal.showLoading();
            fetch('/api/v1/agn/modal')
                .then(r => r.text())
                .then(html => {
                    Swal.getPopup().innerHTML = html;
                    if (window.htmx) { htmx.process(Swal.getPopup()); }
                    if (window.Alpine) { Alpine.initTree(Swal.getPopup()); }
                });
        }
    });
};
</script>"""

# Since spacing might vary, I'll just find where window.openAgnModal is and replace everything up to </script>
content = re.sub(r"window\.openAgnModal = function\(\) \{.*?</script>", new_func, content, flags=re.DOTALL)

with open("app/templates/pages/dashboard.html", "w", encoding="utf-8") as f:
    f.write(content)
