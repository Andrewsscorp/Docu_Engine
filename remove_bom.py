import os

files_to_fix = [
    "app/templates/components/expedientes_grid.html",
    "app/templates/components/expedientes_grid_items.html",
    "app/templates/components/expedientes_module.html",
    "app/routers/agn.py"
]

for filepath in files_to_fix:
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            content = f.read()
        
        # Remove BOM if it exists
        if content.startswith(b'\xef\xbb\xbf'):
            content = content[3:]
            with open(filepath, "wb") as f:
                f.write(content)
            print(f"Removed BOM from {filepath}")
        else:
            print(f"No BOM in {filepath}")
