# auth_routes.py
from fastapi import APIRouter, Depends
import os
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db_session  # Import antiguo temporal para conexión

from backend.src.infrastructure.repositories.postgres_user_repo import PostgresUserRepository
from backend.src.infrastructure.security.bcrypt_hasher import BcryptHashService
from backend.src.infrastructure.security.jwt_service import JWTSettings, JWTTokenService
from backend.src.infrastructure.security.mfa_session_service import InMemoryMfaSessionService
from backend.src.application.use_cases.login_user import LoginUseCase
from backend.src.application.use_cases.verify_mfa import VerifyMfaUseCase
from backend.src.presentation.controllers.auth_controller import AuthController
from backend.src.application.dtos.auth_dtos import (
    LoginRequestDTO,
    LoginResponseDTO,
    MfaVerificationRequestDTO,
)

auth_router = APIRouter(prefix="/api/v2/auth", tags=["Autenticación v2 (Clean Arch)"])
mfa_session_service = InMemoryMfaSessionService()

def get_auth_controller(db: AsyncSession = Depends(get_db_session)) -> AuthController:
    repo = PostgresUserRepository(db)
    hash_srv = BcryptHashService()
    token_srv = JWTTokenService(
        JWTSettings(
            private_key=os.environ["JWT_PRIVATE_KEY"].replace("\\n", "\n"),
            public_key=os.environ["JWT_PUBLIC_KEY"].replace("\\n", "\n"),
            audience=os.environ.get("JWT_AUDIENCE", "docuengine-api"),
            issuer=os.environ.get("JWT_ISSUER", "docuengine-auth"),
            expiration_minutes=int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60")),
        )
    )
    login_use_case = LoginUseCase(repo, hash_srv, token_srv, mfa_session_service)
    verify_mfa_use_case = VerifyMfaUseCase(mfa_session_service, token_srv, repo)
    return AuthController(login_use_case, verify_mfa_use_case)

@auth_router.post("/login", response_model=LoginResponseDTO)
async def login_v2(request: LoginRequestDTO, controller: AuthController = Depends(get_auth_controller)):
    # La ruta es extremadamente delgada
    return await controller.login(request)


@auth_router.post("/verify-mfa", response_model=LoginResponseDTO)
async def verify_mfa(
    request: MfaVerificationRequestDTO,
    controller: AuthController = Depends(get_auth_controller),
):
    return await controller.verify_mfa(request)
