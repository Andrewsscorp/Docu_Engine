# i_security_services.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import timedelta
from typing import Optional


class TokenInvalidError(Exception):
    """Raised when a token is expired, malformed, or invalid."""


@dataclass(frozen=True)
class AccessTokenClaims:
    subject: str
    user_id: str
    tenant_id: str

    def __post_init__(self) -> None:
        for field_name in ("subject", "user_id", "tenant_id"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value:
                raise ValueError(f"{field_name} must be a non-empty string")

class IHashService(ABC):
    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica si una contraseña coincide con su hash."""
        pass
        
    @abstractmethod
    def get_password_hash(self, password: str) -> str:
        """Genera un hash seguro a partir de una contraseña."""
        pass

    @abstractmethod
    def get_dummy_password_hash(self) -> str:
        """Return a valid hash used to equalize unknown-user timings."""
        pass

class ITokenService(ABC):
    @abstractmethod
    def create_access_token(
        self,
        claims: AccessTokenClaims,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Create an access token from validated claims."""
        pass

    @abstractmethod
    def verify_token(self, token: str) -> AccessTokenClaims:
        """Verify and decode a token or raise TokenInvalidError."""
        pass
