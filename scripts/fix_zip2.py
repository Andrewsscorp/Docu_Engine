with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re

# We want to replace from `# Crear ZIP en memoria` until the `return StreamingResponse(...)` block.
pattern = r'# Crear ZIP en memoria.*?return StreamingResponse\([\s\S]*?\)'

new_block = """# Crear ZIP en memoria (Offloaded to threadpool to prevent blocking)
    from fastapi.concurrency import run_in_threadpool
    import json
    
    def create_zip_sync(docs_list, t_id):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            metadata = []
            for d_dict in docs_list:
                full_path = os.path.join("uploads", str(t_id), d_dict["file_path"]).replace("\\\\", "/")
                if os.path.exists(full_path):
                    zip_file.write(full_path, arcname=f"documentos/{d_dict['file_name']}")
                    metadata.append(d_dict)
            zip_file.writestr("metadatos.json", json.dumps(metadata, indent=2))
        zip_buffer.seek(0)
        return zip_buffer

    docs_dicts = [dict(d._mapping) for d in docs]
    zip_buffer = await run_in_threadpool(create_zip_sync, docs_dicts, session_data["tenant_id"])
    
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=Expediente_{exp_code}.zip"}
    )"""

content = re.sub(pattern, new_block, content, flags=re.DOTALL)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
