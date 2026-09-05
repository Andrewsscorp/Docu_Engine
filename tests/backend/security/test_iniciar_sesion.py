# test_iniciar_sesion.py
import pytest
import pyotp
from uuid import UUID
from backend.src.domain.entities.usuario import Usuario
from backend.src.application.dtos.auth_dtos import (
    LoginRequestDTO,
    MfaVerificationRequestDTO,
)
from backend.src.application.use_cases.login_user import LoginUseCase, InvalidCredentialsError
from backend.src.application.use_cases.verify_mfa import VerifyMfaUseCase
from backend.src.domain.interfaces.i_user_repository import IUserRepository
from backend.src.domain.interfaces.i_security_services import IHashService, ITokenService
from backend.src.domain.interfaces.i_security_services import AccessTokenClaims
from backend.src.infrastructure.security.mfa_session_service import InMemoryMfaSessionService
from backend.src.domain.interfaces.i_mfa_session_service import MfaSessionInvalidError

# 1. Mocks de Infraestructura (¡Pruebas sin Base de Datos!)
class MockUserRepository(IUserRepository):
    def __init__(self):
        self.users = {
            "admin": Usuario(
                id="00000000-0000-0000-0000-000000000001",
                username="admin",
                password_hash="hashed_123",
                estado="ACTIVO",
                tenant_id="00000000-0000-0000-0000-000000000010",
            ),
            "inactivo": Usuario(
                id="00000000-0000-0000-0000-000000000002",
                username="inactivo",
                password_hash="hashed_123",
                estado="INACTIVO",
                tenant_id="00000000-0000-0000-0000-000000000010",
            ),
            "mfa": Usuario(
                id="00000000-0000-0000-0000-000000000003",
                username="mfa",
                password_hash="hashed_123",
                estado="ACTIVO",
                tenant_id="00000000-0000-0000-0000-000000000010",
                mfa_secret="JBSWY3DPEHPK3PXP",
            )
        }
        self.last_login_updated_for = None
        
    async def get_by_username(self, username: str):
        return self.users.get(username)

    async def update_last_login(self, user_id: UUID):
        self.last_login_updated_for = user_id

class MockHashService(IHashService):
    def verify_password(self, plain, hashed):
        return plain == "password123" and hashed == "hashed_123"
    def get_password_hash(self, password):
        return "hashed_" + password

    def get_dummy_password_hash(self):
        return "hashed_123"

class MockTokenService(ITokenService):
    def __init__(self):
        self.last_payload_received = None
        self.last_expires_delta = None

    def create_access_token(self, data, expires_delta=None):
        self.last_payload_received = data
        self.last_expires_delta = expires_delta
        return "fake-jwt-token"

    def verify_token(self, token):
        return AccessTokenClaims(token, "", "")

# 2. Configuración del Test
@pytest.fixture
def use_case():
    repo = MockUserRepository()
    hasher = MockHashService()
    tokener = MockTokenService()
    mfa_service = InMemoryMfaSessionService()
    login_use_case = LoginUseCase(repo, hasher, tokener, mfa_service)
    verify_mfa_use_case = VerifyMfaUseCase(mfa_service, tokener, repo)
    return login_use_case, verify_mfa_use_case, repo, tokener

# 3. Casos de Prueba Puros de Dominio
@pytest.mark.asyncio
async def test_login_exitoso(use_case):
    uc, _, repo, tokener = use_case
    req = LoginRequestDTO(username="admin", password="password123")
    res = await uc.execute(req)
    
    assert res.access_token == "fake-jwt-token"
    assert res.token_type == "Bearer"
    assert res.requires_mfa is False
    assert res.mfa_session_id is None
    assert repo.last_login_updated_for == UUID("00000000-0000-0000-0000-000000000001")
    assert tokener.last_payload_received == AccessTokenClaims(
        subject="admin",
        user_id="00000000-0000-0000-0000-000000000001",
        tenant_id="00000000-0000-0000-0000-000000000010",
    )
    assert tokener.last_expires_delta is None


@pytest.mark.asyncio
async def test_login_mfa_does_not_issue_access_token(use_case):
    uc, verify_uc, repo, tokener = use_case
    req = LoginRequestDTO(username="mfa", password="password123")

    res = await uc.execute(req)

    assert res.requires_mfa is True
    assert res.access_token is None
    assert res.token_type is None
    assert res.mfa_session_id
    assert len(res.mfa_session_id) >= 32
    assert tokener.last_payload_received is None
    assert repo.last_login_updated_for is None

    verified = await verify_uc.execute(
        MfaVerificationRequestDTO(
            mfa_session_id=res.mfa_session_id,
            otp_code=pyotp.TOTP("JBSWY3DPEHPK3PXP").now(),
        )
    )

    assert verified.access_token == "fake-jwt-token"
    assert verified.token_type == "Bearer"
    assert repo.last_login_updated_for == UUID(
        "00000000-0000-0000-0000-000000000003"
    )

    with pytest.raises(MfaSessionInvalidError):
        await verify_uc.execute(
            MfaVerificationRequestDTO(
                mfa_session_id=res.mfa_session_id,
                otp_code=pyotp.TOTP("JBSWY3DPEHPK3PXP").now(),
            )
        )


@pytest.mark.asyncio
async def test_mfa_session_is_invalidated_after_three_failed_attempts(use_case):
    uc, verify_uc, _, _ = use_case
    res = await uc.execute(LoginRequestDTO(username="mfa", password="password123"))

    for _ in range(3):
        with pytest.raises(MfaSessionInvalidError):
            await verify_uc.execute(
                MfaVerificationRequestDTO(
                    mfa_session_id=res.mfa_session_id,
                    otp_code="000000",
                )
            )

    with pytest.raises(MfaSessionInvalidError):
        await verify_uc.execute(
            MfaVerificationRequestDTO(
                mfa_session_id=res.mfa_session_id,
                otp_code=pyotp.TOTP("JBSWY3DPEHPK3PXP").now(),
            )
        )

@pytest.mark.asyncio
async def test_login_falla_credenciales_malas(use_case):
    uc, _, _, _ = use_case
    req = LoginRequestDTO(username="admin", password="wrongpass")
    
    with pytest.raises(InvalidCredentialsError):
        await uc.execute(req)

@pytest.mark.asyncio
async def test_login_falla_usuario_no_existe(use_case):
    uc, _, _, _ = use_case
    req = LoginRequestDTO(username="ghost", password="password123")
    
    with pytest.raises(InvalidCredentialsError):
        await uc.execute(req)

@pytest.mark.asyncio
async def test_login_rejects_inactive_user_without_disclosing_state(use_case):
    uc, _, _, _ = use_case
    req = LoginRequestDTO(username="inactivo", password="password123")
    
    with pytest.raises(InvalidCredentialsError, match="Invalid credentials"):
        await uc.execute(req)
