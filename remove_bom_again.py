for filename in ["app/templates/components/expedientes_grid_items.html", "app/templates/components/subseries_module.html"]:
    with open(filename, "rb") as f:
        content = f.read()
    if content.startswith(b"\xef\xbb\xbf"):
        with open(filename, "wb") as f:
            f.write(content[3:])
        print(f"Removed BOM from {filename}")
