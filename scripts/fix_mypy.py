content = """[mypy]
ignore_missing_imports = True
exclude = ^(\.venv|migrations|backups|scripts)/
explicit_package_bases = True
"""
with open("mypy.ini", "w", encoding="utf-8") as f:
    f.write(content)
