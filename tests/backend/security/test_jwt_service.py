from datetime import datetime, timedelta, timezone

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import jwt
import pytest
from backend.src.domain.interfaces.i_security_services import AccessTokenClaims
from backend.src.infrastructure.security.jwt_service import (
    JWTSettings,
    JWTTokenService,
    TokenInvalidError,
)

class MutableClock:
    def __init__(self, current_time):
        self.current_time = current_time

    def __call__(self):
        return self.current_time


@pytest.fixture
def jwt_service():
    clock = MutableClock(datetime(2030, 1, 1, tzinfo=timezone.utc))
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()
    public_pem = private_key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    settings = JWTSettings(
        private_key=private_pem,
        public_key=public_pem,
        expiration_minutes=60,
    )
    return JWTTokenService(settings, clock=clock), clock, private_key


def test_create_and_verify_token(jwt_service):
    service, _, _ = jwt_service
    token = service.create_access_token(
        AccessTokenClaims("usuario-1", "user-1", "tenant-1"),
        expires_delta=timedelta(minutes=5),
    )

    payload = service.verify_token(token)

    assert payload == AccessTokenClaims("usuario-1", "user-1", "tenant-1")


def test_verify_token_rejects_invalid_token(jwt_service):
    service, _, _ = jwt_service
    with pytest.raises(TokenInvalidError, match=JWTTokenService.INVALID_TOKEN_MESSAGE):
        service.verify_token("invalid-token")


def test_verify_token_rejects_expired_token(jwt_service):
    service, clock, _ = jwt_service
    token = service.create_access_token(
        AccessTokenClaims("usuario-1", "user-1", "tenant-1"),
        expires_delta=timedelta(minutes=5),
    )
    clock.current_time += timedelta(minutes=6)

    with pytest.raises(TokenInvalidError, match=JWTTokenService.INVALID_TOKEN_MESSAGE):
        service.verify_token(token)


def test_verify_token_rejects_token_signed_with_wrong_key(jwt_service):
    service, clock, _ = jwt_service
    wrong_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    token = jwt.encode(
        {
            "sub": "usuario-1",
            "user_id": "user-1",
            "tenant_id": "tenant-1",
            "aud": service.audience,
            "iss": service.issuer,
            "iat": clock(),
            "exp": clock() + timedelta(minutes=5),
        },
        wrong_private_key,
        algorithm=service.ALGORITHM,
    )

    with pytest.raises(TokenInvalidError, match=JWTTokenService.INVALID_TOKEN_MESSAGE):
        service.verify_token(token)


def test_verify_token_rejects_wrong_audience(jwt_service):
    service, clock, _ = jwt_service
    token = jwt.encode(
        {
            "sub": "usuario-1",
            "user_id": "user-1",
            "tenant_id": "tenant-1",
            "aud": "another-service",
            "iss": service.issuer,
            "iat": clock(),
            "exp": clock() + timedelta(minutes=5),
        },
        service.settings.private_key,
        algorithm=service.ALGORITHM,
    )

    with pytest.raises(TokenInvalidError, match=JWTTokenService.INVALID_TOKEN_MESSAGE):
        service.verify_token(token)
