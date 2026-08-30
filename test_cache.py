from app.rbac import check_permission, rbac_l1_cache, load_rbac_cache
import asyncio
from app.database import AsyncSessionLocal

async def test():
    async with AsyncSessionLocal() as db:
        await load_rbac_cache(db)
        
    for tenant_id, tenant_data in rbac_l1_cache.items():
        for role_id, role_data in tenant_data["roles"].items():
            print(f"Role: {role_data['name']}, Permisos: {len(role_data['permissions'])}")
            if "tipologias:crear" in role_data["permissions"]:
                print("-> TIENE tipologias:crear")

asyncio.run(test())
