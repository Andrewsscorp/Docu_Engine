import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def apply_migration():
    sql = """
    CREATE MATERIALIZED VIEW vista_fuid_detalle_subserie AS
    SELECT 
        ROW_NUMBER() OVER (
            PARTITION BY exp.subserie_id 
            ORDER BY exp.codigo_expediente ASC
        ) AS no_orden,
        
        exp.codigo_expediente AS codigo,
        exp.nombre_expediente AS nombre_unidad_conservacion,
        
        (SELECT MIN(created_at) 
         FROM documents doc 
         WHERE doc.agn_expediente_id = exp.id 
           AND doc.status IN ('COMPLETED', 'ARCHIVED')) AS fecha_inicial,
           
        (SELECT MAX(created_at) 
         FROM documents doc 
         WHERE doc.agn_expediente_id = exp.id 
           AND doc.status IN ('COMPLETED', 'ARCHIVED')) AS fecha_final,
           
        'N/A' AS caja_carpeta,
        
        COALESCE((SELECT SUM(paginas_cantidad) 
                  FROM documents doc 
                  WHERE doc.agn_expediente_id = exp.id 
                    AND doc.status IN ('COMPLETED', 'ARCHIVED')), 0) AS folios,
                    
        'ELECTRÓNICO' AS soporte,
        exp.subserie_id,
        exp.tenant_id,
        exp.id as exp_id
        
    FROM agn_expedientes exp
    WHERE exp.estado = 'CERRADO';
    
    ALTER MATERIALIZED VIEW vista_fuid_detalle_subserie OWNER TO docuengine_api;
    """
    
    import os
    DB_HOST = os.getenv("DB_HOST", "localhost")
    engine = create_async_engine(f"postgresql+asyncpg://postgres:postgres@{DB_HOST}:5432/docuengine")
    
    async with engine.begin() as conn:
        await conn.execute(text("DROP MATERIALIZED VIEW IF EXISTS vista_fuid_detalle_subserie"))
        await conn.execute(text(sql))
        print("Materialized view created!")

asyncio.run(apply_migration())
