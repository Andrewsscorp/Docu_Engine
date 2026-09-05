from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from backend.src.domain.entities.usuario import Usuario


class MfaSessionInvalidError(Exception):
    """Raised when an MFA session is missing, expired, used, or has an invalid OTP."""


@dataclass(frozen=True)
class MfaSession:
    user_id: UUID
    username: str
    tenant_id: UUID


class IMfaSessionService(ABC):
    @abstractmethod
    async def create_session(self, user: Usuario) -> str:
        pass

    @abstractmethod
    async def verify_and_consume(self, session_id: str, otp_code: str) -> MfaSession:
        pass
