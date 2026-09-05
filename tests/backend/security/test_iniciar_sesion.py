# test_iniciar_sesion.py
import pytest
from backend.src.domain.entities.usuario import Usuario
from backend.src.application.dtos.auth_dtos import LoginRequestDTO
from backend.src.application.use_cases.iniciar_sesion import IniciarSesionUseCase, InvalidCredentialsError, UserInactiveError
from backend.src.domain.interfaces.i_user_repository import IUserRepository
from backend.src.domain.interfaces.i_security_services import IHashService, ITokenService

# 1. Mocks de Infraestructura (¡Pruebas sin Base de Datos!)
class MockUserRepository(IUserRepository):
    def __init__(self):
        self.users = {
            "admin": Usuario(id="1", username="admin", password_hash="hashed_123", estado="ACTIVO", tenant_id="T1"),
            "inactivo": Usuario(id="2", username="inactivo", password_hash="hashed_123", estado="INACTIVO", tenant_id="T1")
        }
        self.last_login_updated_for = None
        
    async def get_by_username(self, username: str):
        return self.users.get(username)

    async def update_last_login(self, user_id: str):
        self.last_login_updated_for = user_id

class MockHashService(IHashService):
    def verify_password(self, plain, hashed):
        return plain == "123" and hashed == "hashed_123"
    def get_password_hash(self, password):
        return "hashed_" + password

class MockTokenService(ITokenService):
    def create_access_token(self, data, mins):
        return "fake-jwt-token"

# 2. Configuración del Test
@pytest.fixture
def use_case():
    repo = MockUserRepository()
    hasher = MockHashService()
    tokener = MockTokenService()
    return IniciarSesionUseCase(repo, hasher, tokener), repo

# 3. Casos de Prueba Puros de Dominio
@pytest.mark.asyncio
async def test_login_exitoso(use_case):
    uc, repo = use_case
    req = LoginRequestDTO(username="admin", password="123")
    res = await uc.execute(req)
    
    assert res.token == "fake-jwt-token"
    assert res.requires_mfa is False
    assert repo.last_login_updated_for == "1"

@pytest.mark.asyncio
async def test_login_falla_credenciales_malas(use_case):
    uc, _ = use_case
    req = LoginRequestDTO(username="admin", password="wrongpassword")
    
    with pytest.raises(InvalidCredentialsError):
        await uc.execute(req)

@pytest.mark.asyncio
async def test_login_falla_usuario_no_existe(use_case):
    uc, _ = use_case
    req = LoginRequestDTO(username="ghost", password="123")
    
    with pytest.raises(InvalidCredentialsError):
        await uc.execute(req)

@pytest.mark.asyncio
async def test_login_falla_usuario_inactivo(use_case):
    uc, _ = use_case
    req = LoginRequestDTO(username="inactivo", password="123")
    
    with pytest.raises(UserInactiveError):
        await uc.execute(req)
