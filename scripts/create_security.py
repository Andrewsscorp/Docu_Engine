import os

files_to_create = {
    # ------------------ DOMAIN ------------------
    "backend/src/domain/entities/usuario.py": """# usuario.py
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
""",
    "backend/src/domain/interfaces/i_user_repository.py": """# i_user_repository.py
from typing import Optional
from abc import ABC, abstractmethod
from backend.src.domain.entities.usuario import Usuario

class IUserRepository(ABC):
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[Usuario]:
        pass

    @abstractmethod
    async def update_last_login(self, user_id: str) -> None:
        pass
""",
    "backend/src/domain/interfaces/i_security_services.py": """# i_security_services.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class IHashService(ABC):
    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        pass
        
    @abstractmethod
    def get_password_hash(self, password: str) -> str:
        pass

class ITokenService(ABC):
    @abstractmethod
    def create_access_token(self, data: Dict[str, Any], expires_delta_minutes: int) -> str:
        pass
""",

    # ------------------ APPLICATION ------------------
    "backend/src/application/dtos/auth_dtos.py": """# auth_dtos.py
from pydantic import BaseModel

class LoginRequestDTO(BaseModel):
    username: str
    password: str

class LoginResponseDTO(BaseModel):
    token: str
    requires_mfa: bool
    user_id: str
""",
    "backend/src/application/use_cases/iniciar_sesion.py": """# iniciar_sesion.py
from backend.src.domain.interfaces.i_user_repository import IUserRepository
from backend.src.domain.interfaces.i_security_services import IHashService, ITokenService
from backend.src.application.dtos.auth_dtos import LoginRequestDTO, LoginResponseDTO

class InvalidCredentialsError(Exception):
    pass

class UserInactiveError(Exception):
    pass

class IniciarSesionUseCase:
    def __init__(
        self, 
        user_repo: IUserRepository, 
        hash_service: IHashService, 
        token_service: ITokenService
    ):
        self.user_repo = user_repo
        self.hash_service = hash_service
        self.token_service = token_service

    async def execute(self, request: LoginRequestDTO) -> LoginResponseDTO:
        user = await self.user_repo.get_by_username(request.username)
        if not user:
            raise InvalidCredentialsError("Credenciales inválidas")

        if not self.hash_service.verify_password(request.password, user.password_hash):
            raise InvalidCredentialsError("Credenciales inválidas")

        if not user.is_active():
            raise UserInactiveError("Usuario inactivo")

        await self.user_repo.update_last_login(user.id)

        requires_mfa = bool(user.mfa_secret)
        
        token = ""
        if not requires_mfa:
            token_data = {"sub": user.username, "user_id": user.id, "tenant_id": user.tenant_id}
            token = self.token_service.create_access_token(token_data, 60)

        return LoginResponseDTO(
            token=token,
            requires_mfa=requires_mfa,
            user_id=user.id
        )
""",

    # ------------------ INFRASTRUCTURE ------------------
    "backend/src/infrastructure/security/bcrypt_hasher.py": """# bcrypt_hasher.py
from passlib.context import CryptContext
from backend.src.domain.interfaces.i_security_services import IHashService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class BcryptHashService(IHashService):
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)
""",
    "backend/src/infrastructure/security/jwt_service.py": """# jwt_service.py
from datetime import datetime, timedelta
import os
import jwt
from typing import Dict, Any
from backend.src.domain.interfaces.i_security_services import ITokenService

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("Missing SECRET_KEY environment variable")
if len(SECRET_KEY) < 32:
    raise ValueError("SECRET_KEY must be at least 32 characters long")
ALGORITHM = "HS256"

class JWTTokenService(ITokenService):
    def create_access_token(self, data: Dict[str, Any], expires_delta_minutes: int) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=expires_delta_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
""",
    "backend/src/infrastructure/repositories/postgres_user_repo.py": """# postgres_user_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional
from backend.src.domain.entities.usuario import Usuario
from backend.src.domain.interfaces.i_user_repository import IUserRepository

class PostgresUserRepository(IUserRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_username(self, username: str) -> Optional[Usuario]:
        query = text(\"""
            SELECT id, username, password_hash, estado, tenant_id, mfa_secret, es_cuenta_servicio 
            FROM usuarios WHERE username = :u
        \""")
        res = await self.db.execute(query, {"u": username})
        row = res.fetchone()
        if not row:
            return None
        
        return Usuario(
            id=str(row.id),
            username=row.username,
            password_hash=row.password_hash,
            estado=row.estado,
            tenant_id=row.tenant_id,
            mfa_secret=row.mfa_secret,
            es_cuenta_servicio=row.es_cuenta_servicio
        )

    async def update_last_login(self, user_id: str) -> None:
        query = text("UPDATE usuarios SET ultimo_acceso = NOW() WHERE id = :id")
        await self.db.execute(query, {"id": user_id})
""",

    # ------------------ PRESENTATION ------------------
    "backend/src/presentation/controllers/auth_controller.py": """# auth_controller.py
from fastapi import HTTPException
from backend.src.application.dtos.auth_dtos import LoginRequestDTO, LoginResponseDTO
from backend.src.application.use_cases.iniciar_sesion import IniciarSesionUseCase, InvalidCredentialsError, UserInactiveError

class AuthController:
    def __init__(self, login_use_case: IniciarSesionUseCase):
        self.login_use_case = login_use_case

    async def login(self, request: LoginRequestDTO) -> LoginResponseDTO:
        try:
            return await self.login_use_case.execute(request)
        except InvalidCredentialsError:
            raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
        except UserInactiveError:
            raise HTTPException(status_code=403, detail="Usuario inactivo")
""",
    "backend/src/presentation/routes/auth_routes.py": """# auth_routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db_session  # Import antiguo temporal para conexión

from backend.src.infrastructure.repositories.postgres_user_repo import PostgresUserRepository
from backend.src.infrastructure.security.bcrypt_hasher import BcryptHashService
from backend.src.infrastructure.security.jwt_service import JWTTokenService
from backend.src.application.use_cases.iniciar_sesion import IniciarSesionUseCase
from backend.src.presentation.controllers.auth_controller import AuthController
from backend.src.application.dtos.auth_dtos import LoginRequestDTO, LoginResponseDTO

auth_router = APIRouter(prefix="/api/v2/auth", tags=["Autenticación v2 (Clean Arch)"])

def get_auth_controller(db: AsyncSession = Depends(get_db_session)) -> AuthController:
    repo = PostgresUserRepository(db)
    hash_srv = BcryptHashService()
    token_srv = JWTTokenService()
    use_case = IniciarSesionUseCase(repo, hash_srv, token_srv)
    return AuthController(use_case)

@auth_router.post("/login", response_model=LoginResponseDTO)
async def login_v2(request: LoginRequestDTO, controller: AuthController = Depends(get_auth_controller)):
    # La ruta es extremadamente delgada
    return await controller.login(request)
""",

    # ------------------ TESTS ------------------
    "tests/backend/security/test_iniciar_sesion.py": """# test_iniciar_sesion.py
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
"""
}

# Create test directory
os.makedirs("tests/backend/security", exist_ok=True)

for path, content in files_to_create.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("All Clean Architecture files created successfully.")
