import asyncio
from app.database import get_global_db_session
from sqlalchemy import text

async def main():
    async for db in get_global_db_session():
        await db.execute(text("""
            CREATE TABLE IF NOT EXISTS agn_expediente_tipologia (
                id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
                expediente_id uuid NOT NULL REFERENCES agn_expedientes(id) ON DELETE CASCADE,
                tipologia_id uuid NOT NULL REFERENCES agn_tipologias(id) ON DELETE CASCADE,
                obligatoria boolean DEFAULT true,
                orden_sugerido integer,
                estado_regla boolean DEFAULT true,
                usuario_creador character varying,
                created_at timestamp with time zone DEFAULT now(),
                UNIQUE(expediente_id, tipologia_id)
            );
        """))
        await db.commit()
        print("Table agn_expediente_tipologia created!")

asyncio.run(main())
