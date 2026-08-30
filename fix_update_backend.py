with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

old_block = """    form_data = await request.form()
    nombre = form_data.get("nombre_expediente")
    resp_id = form_data.get("responsable_id")"""

new_block = """    form_data = await request.form()
    nombre = form_data.get("nombre_expediente")
    resp_id = form_data.get("responsable_id")
    soporte = form_data.get("soporte")"""

content = content.replace(old_block, new_block)

old_update = """    await db.execute(text("UPDATE agn_expedientes SET nombre_expediente = :n, responsable_id = :r WHERE id = :id"), {"n": nombre, "r": resp_id, "id": id})"""

new_update = """    if soporte:
        await db.execute(text("UPDATE agn_expedientes SET nombre_expediente = :n, soporte = :s WHERE id = :id"), {"n": nombre, "s": soporte, "id": id})
    else:
        await db.execute(text("UPDATE agn_expedientes SET nombre_expediente = :n WHERE id = :id"), {"n": nombre, "id": id})"""

content = content.replace(old_update, new_update)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated agn.py update_expediente")
