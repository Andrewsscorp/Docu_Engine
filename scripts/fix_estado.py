with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    agn = f.read()

agn = agn.replace(
    "SET estado = 'CERRADO', \n            fecha_cierre = :fc,",
    "SET estado = 'CERRADO', \n            estado_abierto = FALSE, \n            fecha_cierre = :fc,"
)
with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(agn)
