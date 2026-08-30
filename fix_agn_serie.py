with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

# Add serie_id: str = "" to get_expedientes_module parameters
content = content.replace(
    'subserie_id: str = "",',
    'serie_id: str = "",\n    subserie_id: str = "",'
)

# In Nivel 1 block: 
# if not subserie_id and not serie_id and request.headers.get("hx-target") != "expedientes-results-grid"...
content = content.replace(
    'if not subserie_id and request.headers.get("hx-target") != "expedientes-results-grid"',
    'if not subserie_id and not serie_id and request.headers.get("hx-target") != "expedientes-results-grid"'
)

# In Nivel 2 block:
# add filter for serie_id
filter_sub = '''    if subserie_id:
        where_clauses.append("e.subserie_id = CAST(:subid AS uuid)")
        params["subid"] = subserie_id'''

filter_serie = filter_sub + '''\n    elif serie_id:
        where_clauses.append("e.serie_id = CAST(:serid AS uuid) AND e.subserie_id IS NULL")
        params["serid"] = serie_id'''

content = content.replace(filter_sub, filter_serie)

# In Breadcrumbs block
bc_sub = '''    if subserie_id:
        bc_query = \'\'\'
            SELECT ss.nombre as subserie_nombre, s.nombre as serie_nombre, d.nombre as dep_nombre
            FROM agn_subseries ss
            JOIN agn_series s ON ss.serie_id = s.id
            JOIN agn_dependencias d ON d.id = COALESCE(s.subseccion_id, s.seccion_id)
            WHERE ss.id = CAST(:subid AS uuid)
        \'\'\'
        res_bc = await db.execute(text(bc_query), {"subid": subserie_id})
        bc_row = res_bc.fetchone()
        if bc_row:
            bc = dict(bc_row._mapping)
            import datetime
            breadcrumb = f"Fondo > {bc['dep_nombre']} > {bc['serie_nombre']} > {bc['subserie_nombre']} > Vigencia {datetime.datetime.now().year}"'''

bc_serie = bc_sub + '''
    elif serie_id:
        bc_query = \'\'\'
            SELECT s.nombre as serie_nombre, d.nombre as dep_nombre
            FROM agn_series s
            JOIN agn_dependencias d ON d.id = COALESCE(s.subseccion_id, s.seccion_id)
            WHERE s.id = CAST(:serid AS uuid)
        \'\'\'
        res_bc = await db.execute(text(bc_query), {"serid": serie_id})
        bc_row = res_bc.fetchone()
        if bc_row:
            bc = dict(bc_row._mapping)
            import datetime
            breadcrumb = f"Fondo > {bc['dep_nombre']} > {bc['serie_nombre']} > Vigencia {datetime.datetime.now().year}"'''

content = content.replace(bc_sub, bc_serie)

with open("app/routers/agn.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated agn.py for serie_id")
