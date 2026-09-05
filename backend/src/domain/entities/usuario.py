# usuario.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Usuario:
    id: str
    username: str
    password_hash: str
    estado: str
    tenant_id: str
    mfa_secret: Optional[str] = None
    es_cuenta_servicio: bool = False

    def is_active(self) -> bool:
        return self.estado == 'ACTIVO'
