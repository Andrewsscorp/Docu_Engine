with open("app/templates/pages/expediente_view.html", "r", encoding="utf-8") as f:
    content = f.read()
    start = content.find("upload_direct")
    print(content[start-200:start+600])
