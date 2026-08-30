with open("app/templates/pages/dashboard.html", "r", encoding="utf-8") as f:
    content = f.read()

old_script = """    document.body.addEventListener('htmx:confirm', function(evt) {
        evt.preventDefault();
        Swal.fire({"""

new_script = """    document.body.addEventListener('htmx:confirm', function(evt) {
        if (!evt.detail.question) return; // Only intercept if hx-confirm is actually present
        evt.preventDefault();
        Swal.fire({"""

content = content.replace(old_script, new_script)

with open("app/templates/pages/dashboard.html", "w", encoding="utf-8") as f:
    f.write(content)
