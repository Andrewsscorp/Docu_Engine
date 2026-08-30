with open("app/routers/agn.py", "r", encoding="utf-8") as f:
    content = f.read()

# We need to replace query_sub block
old_query_block = """        query_sub = '''
            SELECT ss.id, ss.codigo as subserie_codigo, ss.nombre as subserie_nombre,
                   s.codigo as serie_codigo, s.nombre as serie_nombre,
                   d.codigo as dep_codigo, d.nombre as dep_nombre,
                   ss.retencion_ag, ss.retencion_ac, ss.disposicion, ss.total_expedientes
            FROM agn_subseries ss
            JOIN agn_series s ON ss.serie_id = s.id
            JOIN agn_dependencias d ON d.id = COALESCE(s.subseccion_id, s.seccion_id)
            WHERE ss.tenant_id = :t
            ORDER BY d.codigo, s.codigo, ss.codigo
        '''
        res_sub = await db.execute(text(query_sub), {"t": tenant_id})
        carpetas = []
        for row in res_sub.fetchall():
            d = dict(row._mapping)
            d["codigo_jerarquico"] = f"{d['dep_codigo']}-{d['serie_codigo']}-{d['subserie_codigo']}"
            carpetas.append(d)"""

new_query_block = """        query_sub = '''
            -- 1. Subseries
            SELECT ss.id as subserie_id, ss.codigo as subserie_codigo, ss.nombre as subserie_nombre,
                   s.id as serie_id, s.codigo as serie_codigo, s.nombre as serie_nombre,
                   d.codigo as dep_codigo, d.nombre as dep_nombre,
                   ss.retencion_ag, ss.retencion_ac, ss.disposicion, ss.total_expedientes,
                   'SUBSERIE' as tipo_carpeta
            FROM agn_subseries ss
            JOIN agn_series s ON ss.serie_id = s.id
            JOIN agn_dependencias d ON d.id = COALESCE(s.subseccion_id, s.seccion_id)
            WHERE ss.tenant_id = :t
            
            UNION ALL
            
            -- 2. Series (como carpetas maestras para expedientes sin subserie)
            SELECT NULL as subserie_id, '' as subserie_codigo, '' as subserie_nombre,
                   s.id as serie_id, s.codigo as serie_codigo, s.nombre as serie_nombre,
                   d.codigo as dep_codigo, d.nombre as dep_nombre,
                   s.retencion_ag, s.retencion_ac, s.disposicion, 
                   (SELECT COUNT(*) FROM agn_expedientes WHERE serie_id = s.id AND subserie_id IS NULL) as total_expedientes,
                   'SERIE' as tipo_carpeta
            FROM agn_series s
            JOIN agn_dependencias d ON d.id = COALESCE(s.subseccion_id, s.seccion_id)
            WHERE s.tenant_id = :t 
              AND (
                  -- Mostrar Serie si no tiene subseries, o si ya tiene expedientes directos
                  NOT EXISTS (SELECT 1 FROM agn_subseries WHERE serie_id = s.id)
                  OR 
                  (SELECT COUNT(*) FROM agn_expedientes WHERE serie_id = s.id AND subserie_id IS NULL) > 0
              )
        '''
        res_sub = await db.execute(text(query_sub), {"t": tenant_id})
        carpetas = []
        for row in res_sub.fetchall():
            d = dict(row._mapping)
            # Orden logico manual si es necesario, o lo hacemos aqui:
            if d['tipo_carpeta'] == 'SUBSERIE':
                d["codigo_jerarquico"] = f"{d['dep_codigo']}-{d['serie_codigo']}-{d['subserie_codigo']}"
                d["nombre_mostrar"] = d["subserie_nombre"]
                d["filtro_id"] = f"&subserie_id={d['subserie_id']}"
            else:
                d["codigo_jerarquico"] = f"{d['dep_codigo']}-{d['serie_codigo']}"
                d["nombre_mostrar"] = d["serie_nombre"]
                d["filtro_id"] = f"&serie_id={d['serie_id']}&subserie_id="
            carpetas.append(d)
            
        # Sort carpetas by codigo_jerarquico
        carpetas.sort(key=lambda x: x["codigo_jerarquico"])"""

import re
if "query_sub =" in content:
    content = content.replace(old_query_block, new_query_block)
    with open("app/routers/agn.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Replaced query_sub successfully")
else:
    print("Could not find old_query_block")
