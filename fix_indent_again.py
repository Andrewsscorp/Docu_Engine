with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

bad_str = "            import datetime\nbreadcrumb ="
good_str = "            import datetime\n            breadcrumb ="

content = content.replace(bad_str, good_str)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed indentation")
