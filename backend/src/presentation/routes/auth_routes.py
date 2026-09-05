# auth_routes.py
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
