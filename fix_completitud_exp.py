with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

import re

# Let's find where the index logic starts
idx_match = re.search(r'# 3\. [^\n]+ndice Electr[^\n]+nico\s+idx_res = await db\.execute', content)
if idx_match:
    old_calc = idx_match.group(0)
    new_calc = """# 2.5 Completitud TRD
    matrix_res = await db.execute(text('''
        SELECT 
            st.obligatoria,
            doc.id as documento_id
        FROM agn_subserie_tipologia st
        INNER JOIN agn_tipologias t ON st.tipologia_id = t.id
        LEFT JOIN documents doc ON st.tipologia_id = doc.tipologia_id AND doc.agn_expediente_id = :eid AND (doc.status = 'COMPLETED' OR doc.status = 'ARCHIVED')
        WHERE st.subserie_id = :sid
    '''), {"eid": expediente_id, "sid": exp.get("subserie_id")})
    
    requeridas = 0
    completadas = 0
    
    for row in matrix_res.fetchall():
        r = dict(row._mapping)
        if r["obligatoria"]:
            requeridas += 1
            if r["documento_id"]:
                completadas += 1
                
    completitud_pct = int((completadas / requeridas * 100)) if requeridas > 0 else 100
    
    """ + old_calc
    content = content.replace(old_calc, new_calc)

    old_template = """        "eventos": eventos,
        "completitud_pct": 0,
        "requeridas": 1,
        "completadas": 0
    })"""
    new_template = """        "eventos": eventos,
        "completitud_pct": completitud_pct,
        "requeridas": requeridas,
        "completadas": completadas
    })"""
    content = content.replace(old_template, new_template)

    with open("app/routers/agn.py", "w", encoding="utf-8") as f:
        f.write(content)
else:
    print("Regex failed to find the spot!")
