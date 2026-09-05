with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re

old_block = """    # 2. Extract pages using PyMuPDF
    pages = 1
    if file_path.lower().endswith('.pdf'):
        try:
            with fitz.open(file_path) as pdf_doc:
                pages = len(pdf_doc)
        except Exception:
            pages = 1
            
    # 3. Calculate Hash
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    doc_hash = sha256_hash.hexdigest()"""

new_block = """    from fastapi.concurrency import run_in_threadpool
    
    def process_file_sync(fpath):
        import fitz
        import hashlib
        
        pages_count = 1
        if fpath.lower().endswith('.pdf'):
            try:
                with fitz.open(fpath) as pdf_doc:
                    pages_count = len(pdf_doc)
            except Exception:
                pages_count = 1
                
        sha256_hash = hashlib.sha256()
        with open(fpath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
                
        return pages_count, sha256_hash.hexdigest()

    # 2 & 3. Extract pages & Calculate Hash in Threadpool to avoid blocking
    pages, doc_hash = await run_in_threadpool(process_file_sync, file_path)"""

content = content.replace(old_block, new_block)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
