with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

old_query = """        SELECT 1 FROM user_groups ug
        JOIN groups g ON ug.group_id = g.id
        JOIN role_permissions rp ON g.role_id = rp.role_id
        JOIN permissions p ON rp.permission_id = p.id
        WHERE ug.user_id = :uid AND p.name = 'tipologias:crear'"""

new_query = """        SELECT 1 FROM users u
        JOIN role_permissions rp ON u.role_id = rp.role_id
        JOIN permissions p ON rp.permission_id = p.id
        WHERE u.id = :uid AND p.name = 'tipologias:crear'"""

content = content.replace(old_query, new_query)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
