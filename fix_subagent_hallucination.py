import re

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # The subagent likely injected something like:
    # "SELECT u.id, r.nombre as rol_nombre FROM api_keys_servicio ak JOIN usuarios u ON ... JOIN usuario_roles ... JOIN roles"
    
    # Let's just find where api_keys_servicio is queried and replace the query
    
    content = content.replace("JOIN usuarios u ON u.id = ak.usuario_id", "JOIN users u ON u.id = ak.usuario_id")
    content = content.replace("JOIN usuario_roles ur ON ur.usuario_id = u.id", "")
    content = content.replace("JOIN roles r ON r.id = ur.rol_id", "JOIN roles r ON r.id = u.role_id")
    content = content.replace("r.nombre", "r.name")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

fix_file('app/main.py')
fix_file('app/security.py')
print("Fixed main.py and security.py")
