import asyncio
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict

import pyotp

from backend.src.domain.entities.usuario import Usuario
from backend.src.domain.interfaces.i_mfa_session_service import (
    IMfaSessionService,
    MfaSession,
    MfaSessionInvalidError,
)


@dataclass(frozen=True)
class _StoredMfaSession:
    session: MfaSession
    secret: str
    expires_at: datetime
    failed_attempts: int = 0


class InMemoryMfaSessionService(IMfaSessionService):
    def __init__(self, ttl: timedelta = timedelta(minutes=5)):
        self._sessions: Dict[str, _StoredMfaSession] = {}
        self._ttl = ttl
        self._lock = asyncio.Lock()

    async def create_session(self, user: Usuario) -> str:
        session_id = secrets.token_urlsafe(32)
        session = MfaSession(
            user_id=user.id,
            username=user.username,
            tenant_id=user.tenant_id,
        )
        stored = _StoredMfaSession(
            session=session,
            secret=user.mfa_secret or "",
            expires_at=datetime.now(timezone.utc) + self._ttl,
        )
        async with self._lock:
            self._sessions[session_id] = stored
        return session_id

    async def verify_and_consume(self, session_id: str, otp_code: str) -> MfaSession:
        async with self._lock:
            stored = self._sessions.get(session_id)
            now = datetime.now(timezone.utc)
            if not stored or stored.expires_at <= now:
                self._sessions.pop(session_id, None)
                raise MfaSessionInvalidError("Invalid or expired MFA session")
            if not pyotp.TOTP(stored.secret).verify(otp_code, valid_window=1):
                if stored.failed_attempts + 1 >= 3:
                    del self._sessions[session_id]
                else:
                    self._sessions[session_id] = _StoredMfaSession(
                        session=stored.session,
                        secret=stored.secret,
                        expires_at=stored.expires_at,
                        failed_attempts=stored.failed_attempts + 1,
                    )
                raise MfaSessionInvalidError("Invalid MFA code")
            del self._sessions[session_id]
            return stored.session
