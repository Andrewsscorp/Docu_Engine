# jwt_service.py
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import jwt
from typing import Callable, Optional
from backend.src.domain.interfaces.i_security_services import (
    AccessTokenClaims,
    ITokenService,
    TokenInvalidError,
)


@dataclass(frozen=True)
class JWTSettings:
    private_key: str
    public_key: str
    audience: str = "docuengine-api"
    issuer: str = "docuengine-auth"
    algorithm: str = "RS256"
    expiration_minutes: int = 60

class JWTTokenService(ITokenService):
    INVALID_TOKEN_MESSAGE = "Invalid or expired token"
    ALGORITHM = "RS256"

    def __init__(
        self,
        settings: JWTSettings,
        clock: Optional[Callable[[], datetime]] = None,
    ):
        if not settings.private_key or not settings.public_key:
            raise ValueError("JWT private and public keys are required")
        if settings.algorithm != self.ALGORITHM:
            raise ValueError("Only RS256 is supported")
        if not settings.audience or not settings.issuer:
            raise ValueError("JWT audience and issuer are required")
        if settings.expiration_minutes <= 0:
            raise ValueError("JWT expiration must be positive")
        self.settings = settings
        self.audience = settings.audience
        self.issuer = settings.issuer
        self.default_expiration = timedelta(minutes=settings.expiration_minutes)
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def create_access_token(
        self,
        claims: AccessTokenClaims,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        issued_at = self.clock()
        expire = issued_at + (expires_delta or self.default_expiration)
        payload = {
            "sub": claims.subject,
            "user_id": claims.user_id,
            "tenant_id": claims.tenant_id,
            "aud": self.audience,
            "iss": self.issuer,
            "iat": issued_at,
            "exp": expire,
        }
        encoded_jwt = jwt.encode(
            payload, self.settings.private_key, algorithm=self.ALGORITHM
        )
        return encoded_jwt

    def verify_token(self, token: str) -> AccessTokenClaims:
        try:
            payload = jwt.decode(
                token,
                self.settings.public_key,
                algorithms=[self.ALGORITHM],
                audience=self.audience,
                issuer=self.issuer,
                options={
                    "verify_exp": False,
                    "verify_iat": False,
                    "require": [
                        "sub",
                        "user_id",
                        "tenant_id",
                        "aud",
                        "iss",
                        "iat",
                        "exp",
                    ],
                },
            )
            now = self.clock()
            expiration = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
            issued_at = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
            if expiration <= now or issued_at > now:
                raise TokenInvalidError(self.INVALID_TOKEN_MESSAGE)
            return AccessTokenClaims(
                subject=payload["sub"],
                user_id=payload["user_id"],
                tenant_id=payload["tenant_id"],
            )
        except (jwt.PyJWTError, KeyError, TypeError, ValueError, OverflowError) as exc:
            raise TokenInvalidError(self.INVALID_TOKEN_MESSAGE) from exc
