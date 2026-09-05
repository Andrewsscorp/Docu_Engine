with open("app/routers/documents.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add `agn_expediente_id: str = "",` to the function signature
signature_old = """async def explorer_view(
    request: Request,
    q: str = "",
    sort: str = "desc",
    view: str = "grid",
    group_id: str = "",
    status: str = "",
    page: int = 1,
    folder_filter: str = "",
    type_filter: str = "",
    date_filter: str = "",
    db: AsyncSession = Depends(get_db_session)
):"""
signature_new = """async def explorer_view(
    request: Request,
    q: str = "",
    sort: str = "desc",
    view: str = "grid",
    group_id: str = "",
    status: str = "",
    page: int = 1,
    folder_filter: str = "",
    type_filter: str = "",
    date_filter: str = "",
    agn_expediente_id: str = "",
    db: AsyncSession = Depends(get_db_session)
):"""
content = content.replace(signature_old, signature_new)

# 2. Add SQL filter
filter_old = """    if folder_filter:
        base_query += " AND d.folder_id = :f"
        params["f"] = folder_filter"""
filter_new = """    if folder_filter:
        base_query += " AND d.folder_id = :f"
        params["f"] = folder_filter
        
    if agn_expediente_id:
        base_query += " AND d.agn_expediente_id = :agn_exp"
        params["agn_exp"] = agn_expediente_id"""
content = content.replace(filter_old, filter_new)

# 3. Add to context dict
context_old = """"folder_filter": folder_filter,"""
context_new = """"folder_filter": folder_filter,
        "agn_expediente_id": agn_expediente_id,"""
content = content.replace(context_old, context_new)

with open("app/routers/documents.py", "w", encoding="utf-8") as f:
    f.write(content)
