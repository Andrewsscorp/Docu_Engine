from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Dict, Set

# L1 Cache Structure
# rbac_l1_cache = {
#     tenant_id: {
#         "roles": {
#             role_id: {
#                 "name": str,
#                 "hierarchy": int,
#                 "permissions": { "usuarios:crear", "ajustes:modificar", ... }
#             }
#         }
#     }
# }

rbac_l1_cache: Dict[str, Dict] = {}

async def load_rbac_cache(db: AsyncSession = None):
    
    from app.database import get_global_db_session
    
    new_cache = {}
    
    async for temp_db in get_global_db_session():
        # 1. Fetch all roles
        query_roles = text("SELECT id, tenant_id, name, hierarchy_level FROM roles")
        roles_result = await temp_db.execute(query_roles)
        
        for row in roles_result.fetchall():
            role_id = str(row[0])
            tenant_id = str(row[1])
            name = row[2]
            hierarchy = row[3]
            
            if tenant_id not in new_cache:
                new_cache[tenant_id] = {"roles": {}, "groups": {}, "user_groups": {}}
                
            new_cache[tenant_id]["roles"][role_id] = {
                "name": name,
                "hierarchy": hierarchy,
                "permissions": set()
            }

        # 2. Fetch all role permissions
        query_perms = text("""
            SELECT rp.role_id, p.name 
            FROM role_permissions rp
            JOIN permissions p ON rp.permission_id = p.id
        """)
        perms_result = await temp_db.execute(query_perms)
        
        for row in perms_result.fetchall():
            role_id = str(row[0])
            perm_name = row[1]
            
            # Encontramos a que tenant pertenece el rol
            for tenant_id, tenant_data in new_cache.items():
                if role_id in tenant_data["roles"]:
                    tenant_data["roles"][role_id]["permissions"].add(perm_name)
                    break
                    
        # 3. Fetch all groups
        query_groups = text("SELECT id, tenant_id, name, role_id FROM groups")
        groups_result = await temp_db.execute(query_groups)
        
        for row in groups_result.fetchall():
            group_id = str(row[0])
            tenant_id = str(row[1])
            name = row[2]
            role_id = str(row[3]) if row[3] else None
            
            if tenant_id in new_cache:
                new_cache[tenant_id]["groups"][group_id] = {
                    "name": name,
                    "role_id": role_id
                }

        # 4. Fetch all user_groups
        query_user_groups = text("SELECT user_id, group_id FROM user_groups")
        user_groups_result = await temp_db.execute(query_user_groups)
        
        for row in user_groups_result.fetchall():
            user_id = str(row[0])
            group_id = str(row[1])
            
            # Encontramos a que tenant pertenece el grupo
            for tenant_id, tenant_data in new_cache.items():
                if group_id in tenant_data["groups"]:
                    if user_id not in tenant_data["user_groups"]:
                        tenant_data["user_groups"][user_id] = set()
                    tenant_data["user_groups"][user_id].add(group_id)
                    break
        
        # Break since we only need the first session from the generator
        break

    rbac_l1_cache.clear()
    rbac_l1_cache.update(new_cache)
    print("RBAC L1 Cache Cargado Exitosamente:", {t: len(data["roles"]) for t, data in rbac_l1_cache.items()})

def check_permission(tenant_id: str, role_id: str, required_action: str) -> bool:
    """Verifica en caché L1 (O(1)) si el rol tiene el permiso exacto."""
    if tenant_id not in rbac_l1_cache:
        return False
    if role_id not in rbac_l1_cache[tenant_id]["roles"]:
        return False
    return required_action in rbac_l1_cache[tenant_id]["roles"][role_id]["permissions"]

def get_role_hierarchy(tenant_id: str, role_id: str) -> int:
    """Retorna la jerarquía del rol en caché L1 (O(1))."""
    if tenant_id not in rbac_l1_cache:
        return 0
    if role_id not in rbac_l1_cache[tenant_id]["roles"]:
        return 0
    return rbac_l1_cache[tenant_id]["roles"][role_id]["hierarchy"]

def get_user_groups(tenant_id: str, user_id: str) -> Set[str]:
    if tenant_id not in rbac_l1_cache:
        return set()
    return rbac_l1_cache[tenant_id].get("user_groups", {}).get(user_id, set())

def can_modify_hierarchy(tenant_id: str, actor_role_id: str, target_role_id: str) -> bool:
    """Verifica si el rol actor puede modificar al rol objetivo basándose en jerarquía."""
    actor_level = get_role_hierarchy(tenant_id, actor_role_id)
    target_level = get_role_hierarchy(tenant_id, target_role_id)
    
    # 99 puede modificar a 10. 10 no puede modificar a 99.
    return actor_level > target_level

async def log_audit_action(db: AsyncSession, tenant_id: str, user_id: str, action: str, target_id: str = None, details: dict = None):
    import json
    query = text("""
        INSERT INTO audit_rbac_logs (tenant_id, action, target_id, performed_by_user_id, details)
        VALUES (:tenant, :action, :target, :user_id, :details)
    """)
    await db.execute(query, {
        "tenant": tenant_id,
        "action": action,
        "target": target_id,
        "user_id": user_id,
        "details": json.dumps(details) if details else None
    })
