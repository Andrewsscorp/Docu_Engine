with open("migrations/005_append_only_audit.sql", "r", encoding="utf-8-sig") as f:
    text = f.read()
with open("migrations/005_append_only_audit.sql", "w", encoding="utf-8") as f:
    f.write(text)
