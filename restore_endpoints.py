with open("agn_old.py", "r", encoding="utf-16") as f:
    content = f.read()

start_str = '@router.get("/expedientes/{expediente_id}/control_tipologias")'
end_str = 'return JSONResponse({"status": "success"})\n'

start_idx = content.find(start_str)
end_idx = content.find(end_str, start_idx) + len(end_str)

missing_code = content[start_idx:end_idx]

with open("app/routers/agn.py", "a", encoding="utf-8") as f:
    f.write("\n" + missing_code)
