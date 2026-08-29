import asyncio
from sqlalchemy import text
from app.database import get_global_db_session

async def insert_permission():
    async for db in get_global_db_session():
        # Check if permission exists
        res = await db.execute(text("SELECT id FROM permissions WHERE name = 'documentos:crear'"))
        perm_id = res.scalar()
        
        if not perm_id:
            print("Inserting permission documentos:crear...")
            res = await db.execute(text("INSERT INTO permissions (name, description) VALUES ('documentos:crear', 'Permite crear nuevos expedientes o carpetas') RETURNING id"))
            perm_id = res.scalar()
            
        # Get all roles
        res = await db.execute(text("SELECT id FROM roles"))
        roles = res.fetchall()
        
        for r in roles:
            role_id = r[0]
            # Check if mapped
            mapped = await db.execute(text("SELECT 1 FROM role_permissions WHERE role_id = :r AND permission_id = :p"), {"r": role_id, "p": perm_id})
            if not mapped.scalar():
                print(f"Granting to role {role_id}")
                await db.execute(text("INSERT INTO role_permissions (role_id, permission_id) VALUES (:r, :p)"), {"r": role_id, "p": perm_id})
                
        await db.commit()
        print("Done!")
        break

if __name__ == '__main__':
    asyncio.run(insert_permission())
