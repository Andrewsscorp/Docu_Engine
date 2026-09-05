import asyncio
import uuid
from sqlalchemy import text
from dotenv import load_dotenv
load_dotenv()
from app.database import AsyncSessionLocal

async def seed():
    async with AsyncSessionLocal() as session:
        tenant_id = "22222222-2222-2222-2222-222222222222"
        
        # Insert admin user to satisfy FK
        responsable_id = "11111111-1111-1111-1111-111111111111"
        try:
            await session.execute(text("""
                INSERT INTO users (id, tenant_id, username, email, hash_password, full_name, role_id, is_active, mfa_enabled, require_password_change) 
                VALUES (:id, :t, 'admin_mock', 'a@a.com', 'hash', 'Admin', 2, true, false, false)
                ON CONFLICT DO NOTHING
            """), {"id": responsable_id, "t": tenant_id})
            await session.commit()
        except Exception as e:
            await session.rollback()
            
        # Try finding a user ID if we couldn't insert
        res = await session.execute(text("SELECT id FROM users LIMIT 1"))
        u = res.fetchone()
        if u:
            responsable_id = u.id
            
        # Insert Fondo (100 - Gobernación)
        fondo_id = str(uuid.uuid4())
        await session.execute(text("""
            INSERT INTO agn_dependencias (id, tenant_id, codigo, nombre, tipo) 
            VALUES (:id, :t, '100', 'Gobernación', 'FONDO')
            ON CONFLICT DO NOTHING
        """), {"id": fondo_id, "t": tenant_id})
        
        # Get Fondo ID
        res = await session.execute(text("SELECT id FROM agn_dependencias WHERE tipo='FONDO' AND tenant_id=:t LIMIT 1"), {"t": tenant_id})
        f = res.fetchone()
        fondo_id = f.id if f else fondo_id

        # Insert Seccion (110 - Oficina Jurídica)
        seccion_id = str(uuid.uuid4())
        await session.execute(text("""
            INSERT INTO agn_dependencias (id, tenant_id, codigo, nombre, tipo, parent_id) 
            VALUES (:id, :t, '110', 'Oficina Jurídica', 'SECCION', :f)
            ON CONFLICT DO NOTHING
        """), {"id": seccion_id, "t": tenant_id, "f": fondo_id})
        
        res = await session.execute(text("SELECT id FROM agn_dependencias WHERE tipo='SECCION' AND tenant_id=:t LIMIT 1"), {"t": tenant_id})
        s_row = res.fetchone()
        seccion_id = s_row.id if s_row else seccion_id
        
        # Insert Serie (110-15 - Conceptos Jurídicos)
        serie_id = str(uuid.uuid4())
        await session.execute(text("""
            INSERT INTO agn_series (id, tenant_id, fondo_id, seccion_id, codigo, nombre) 
            VALUES (:id, :t, :f, :s, '110-15', 'Conceptos Jurídicos')
            ON CONFLICT DO NOTHING
        """), {"id": serie_id, "t": tenant_id, "f": fondo_id, "s": seccion_id})
        
        res = await session.execute(text("SELECT id FROM agn_series WHERE tenant_id=:t LIMIT 1"), {"t": tenant_id})
        ser_row = res.fetchone()
        serie_id = ser_row.id if ser_row else serie_id
        
        # Insert Subserie (110-15.01 - Conceptos de Contratación)
        subserie_id = str(uuid.uuid4())
        await session.execute(text("""
            INSERT INTO agn_subseries (id, tenant_id, serie_id, codigo, nombre) 
            VALUES (:id, :t, :s, '110-15.01', 'Conceptos de Contratación')
            ON CONFLICT DO NOTHING
        """), {"id": subserie_id, "t": tenant_id, "s": serie_id})
        
        res = await session.execute(text("SELECT id FROM agn_subseries WHERE tenant_id=:t LIMIT 1"), {"t": tenant_id})
        subser_row = res.fetchone()
        subserie_id = subser_row.id if subser_row else subserie_id
        
        # Insert Expediente (110-15.01-001 - Expediente Contratación 2026)
        expediente_id = str(uuid.uuid4())
        await session.execute(text("""
            INSERT INTO agn_expedientes (id, tenant_id, fondo_id, seccion_id, serie_id, subserie_id, codigo_expediente, nombre_expediente, estado, fecha_apertura, responsable_id) 
            VALUES (:id, :t, :f, :sec, :serie_id, :s, '110-15.01-001', 'Expediente Contratación 2026', 'ABIERTO', CURRENT_TIMESTAMP, :r)
            ON CONFLICT DO NOTHING
        """), {"id": expediente_id, "t": tenant_id, "f": fondo_id, "sec": seccion_id, "serie_id": serie_id, "s": subserie_id, "r": responsable_id})
        
        await session.commit()
        print("Estructura AGN TRD creada exitosamente!")

if __name__ == "__main__":
    asyncio.run(seed())
