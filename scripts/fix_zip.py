with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re

old_block = """    # Crear ZIP en memoria
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        metadata = []
        for d in docs:
            d_dict = dict(d._mapping)
            full_path = os.path.join("uploads", str(session_data["tenant_id"]), d_dict["file_path"]).replace("\\\\", "/")
            if os.path.exists(full_path):
                # Write to zip
                zip_file.write(full_path, arcname=f"documentos/{d_dict['file_name']}")
                metadata.append(d_dict)
                
        # Also generate a metadata JSON
        import json
        zip_file.writestr("metadatos.json", json.dumps(metadata, indent=2))
        
    zip_buffer.seek(0)
    
    # Send ZIP response
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=Expediente_{exp_code}.zip"}
    )"""

new_block = """    from fastapi.concurrency import run_in_threadpool
    import json
    
    def create_zip_sync(docs_list, t_id):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            metadata = []
            for d_dict in docs_list:
                full_path = os.path.join("uploads", str(t_id), d_dict["file_path"]).replace("\\\\", "/")
                if os.path.exists(full_path):
                    # Write to zip
                    zip_file.write(full_path, arcname=f"documentos/{d_dict['file_name']}")
                    metadata.append(d_dict)
            # Generate a metadata JSON
            zip_file.writestr("metadatos.json", json.dumps(metadata, indent=2))
        zip_buffer.seek(0)
        return zip_buffer

    # Offload the blocking zip creation
    docs_dicts = [dict(d._mapping) for d in docs]
    zip_buffer = await run_in_threadpool(create_zip_sync, docs_dicts, session_data["tenant_id"])
    
    # Send ZIP response
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=Expediente_{exp_code}.zip"}
    )"""

# In the actual file it uses single slashes for replace because it's python string: replace("\\", "/")
# So I should use the correct replace. Let's do it carefully.
