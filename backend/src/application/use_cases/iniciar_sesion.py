# iniciar_sesion.py
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
