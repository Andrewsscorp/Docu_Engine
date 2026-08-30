import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://postgres:superadmin_password@localhost:5432/docuengine"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def main():
    statements = [
        "ALTER TABLE agn_subseries ADD COLUMN IF NOT EXISTS total_expedientes INTEGER DEFAULT 0;",
        """
        UPDATE agn_subseries 
        SET total_expedientes = (
            SELECT COUNT(*) FROM agn_expedientes 
            WHERE agn_expedientes.subserie_id = agn_subseries.id 
        );
        """,
        """
        CREATE OR REPLACE FUNCTION trg_func_actualizar_conteo_subserie()
        RETURNS TRIGGER AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                IF NEW.subserie_id IS NOT NULL THEN
                    UPDATE agn_subseries SET total_expedientes = total_expedientes + 1 WHERE id = NEW.subserie_id;
                END IF;
                RETURN NEW;
            ELSIF TG_OP = 'DELETE' THEN
                IF OLD.subserie_id IS NOT NULL THEN
                    UPDATE agn_subseries SET total_expedientes = total_expedientes - 1 WHERE id = OLD.subserie_id;
                END IF;
                RETURN OLD;
            ELSIF TG_OP = 'UPDATE' THEN
                IF NEW.subserie_id IS DISTINCT FROM OLD.subserie_id THEN
                    IF OLD.subserie_id IS NOT NULL THEN
                        UPDATE agn_subseries SET total_expedientes = total_expedientes - 1 WHERE id = OLD.subserie_id;
                    END IF;
                    IF NEW.subserie_id IS NOT NULL THEN
                        UPDATE agn_subseries SET total_expedientes = total_expedientes + 1 WHERE id = NEW.subserie_id;
                    END IF;
                END IF;
                RETURN NEW;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """,
        "DROP TRIGGER IF EXISTS trg_actualizar_conteo_subserie ON agn_expedientes;",
        """
        CREATE TRIGGER trg_actualizar_conteo_subserie
        AFTER INSERT OR UPDATE OR DELETE ON agn_expedientes
        FOR EACH ROW
        EXECUTE FUNCTION trg_func_actualizar_conteo_subserie();
        """
    ]

    async with async_session() as session:
        for stmt in statements:
            await session.execute(text(stmt))
        await session.commit()
        print("Migration for Subseries drilldown applied successfully!")

asyncio.run(main())
