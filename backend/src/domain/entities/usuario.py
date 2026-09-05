# usuario.py
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from uuid import UUID


class EstadoUsuario(str, Enum):
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"
    BLOQUEADO = "BLOQUEADO"

@dataclass
class Usuario:
    id: UUID
    username: str
    password_hash: str = field(repr=False, compare=False)
    estado: EstadoUsuario
    tenant_id: UUID
    mfa_secret: Optional[str] = field(default=None, repr=False, compare=False)
    es_cuenta_servicio: bool = False

    def __post_init__(self) -> None:
        try:
            self.id = UUID(str(self.id))
            self.tenant_id = UUID(str(self.tenant_id))
            self.estado = EstadoUsuario(self.estado)
        except (TypeError, ValueError) as exc:
            raise ValueError("Usuario contiene un UUID o estado inválido") from exc

        if not isinstance(self.username, str) or not 1 <= len(self.username) <= 254:
            raise ValueError("username debe tener entre 1 y 254 caracteres")
        if not isinstance(self.password_hash, str) or len(self.password_hash) > 255:
            raise ValueError("password_hash inválido o demasiado largo")
        if self.mfa_secret is not None and (
            not isinstance(self.mfa_secret, str) or len(self.mfa_secret) > 128
        ):
            raise ValueError("mfa_secret no puede superar 128 caracteres")
        if not isinstance(self.es_cuenta_servicio, bool):
            raise ValueError("es_cuenta_servicio debe ser un booleano")

    def is_active(self) -> bool:
        return self.estado == EstadoUsuario.ACTIVO
