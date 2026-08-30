import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://postgres:superadmin_password@localhost:5432/docuengine"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def main():
    statements = [
        "ALTER TABLE agn_expedientes ADD COLUMN IF NOT EXISTS cantidad_documentos INTEGER DEFAULT 0;",
        "ALTER TABLE agn_expedientes ADD COLUMN IF NOT EXISTS estado_abierto BOOLEAN DEFAULT TRUE;",
        "ALTER TABLE agn_expedientes ADD COLUMN IF NOT EXISTS fase_archivo VARCHAR(50) DEFAULT 'GESTION';",
        """
        UPDATE agn_expedientes 
        SET cantidad_documentos = (
            SELECT COUNT(*) FROM documents 
            WHERE documents.agn_expediente_id = agn_expedientes.id 
        );
        """,
        "DROP INDEX IF EXISTS idx_agn_exp_fts;",
        "CREATE INDEX idx_agn_exp_fts ON agn_expedientes USING GIN (to_tsvector('spanish', coalesce(codigo_expediente, '') || ' ' || coalesce(nombre_expediente, '')));",
        """
        CREATE OR REPLACE FUNCTION trg_func_actualizar_conteo_expediente()
        RETURNS TRIGGER AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                IF NEW.agn_expediente_id IS NOT NULL AND NEW.status != 'FAILED' THEN
                    UPDATE agn_expedientes SET cantidad_documentos = cantidad_documentos + 1 WHERE id = NEW.agn_expediente_id;
                END IF;
                RETURN NEW;
            ELSIF TG_OP = 'DELETE' THEN
                IF OLD.agn_expediente_id IS NOT NULL AND OLD.status != 'FAILED' THEN
                    UPDATE agn_expedientes SET cantidad_documentos = cantidad_documentos - 1 WHERE id = OLD.agn_expediente_id;
                END IF;
                RETURN OLD;
            ELSIF TG_OP = 'UPDATE' THEN
                IF NEW.agn_expediente_id IS DISTINCT FROM OLD.agn_expediente_id THEN
                    IF OLD.agn_expediente_id IS NOT NULL AND OLD.status != 'FAILED' THEN
                        UPDATE agn_expedientes SET cantidad_documentos = cantidad_documentos - 1 WHERE id = OLD.agn_expediente_id;
                    END IF;
                    IF NEW.agn_expediente_id IS NOT NULL AND NEW.status != 'FAILED' THEN
                        UPDATE agn_expedientes SET cantidad_documentos = cantidad_documentos + 1 WHERE id = NEW.agn_expediente_id;
                    END IF;
                ELSE
                    IF OLD.status = 'FAILED' AND NEW.status != 'FAILED' AND NEW.agn_expediente_id IS NOT NULL THEN
                        UPDATE agn_expedientes SET cantidad_documentos = cantidad_documentos + 1 WHERE id = NEW.agn_expediente_id;
                    ELSIF OLD.status != 'FAILED' AND NEW.status = 'FAILED' AND NEW.agn_expediente_id IS NOT NULL THEN
                        UPDATE agn_expedientes SET cantidad_documentos = cantidad_documentos - 1 WHERE id = NEW.agn_expediente_id;
                    END IF;
                END IF;
                RETURN NEW;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """,
        "DROP TRIGGER IF EXISTS trg_actualizar_conteo_expediente ON documents;",
        """
        CREATE TRIGGER trg_actualizar_conteo_expediente
        AFTER INSERT OR UPDATE OR DELETE ON documents
        FOR EACH ROW
        EXECUTE FUNCTION trg_func_actualizar_conteo_expediente();
        """
    ]

    async with async_session() as session:
        for stmt in statements:
            await session.execute(text(stmt))
        await session.commit()
        print("Migration applied successfully!")

asyncio.run(main())
