from backend.src.application.dtos.auth_dtos import LoginRequestDTO, LoginResponseDTO
from backend.src.domain.interfaces.i_mfa_session_service import IMfaSessionService
from backend.src.domain.interfaces.i_security_services import (
    AccessTokenClaims,
    IHashService,
    ITokenService,
)
from backend.src.domain.interfaces.i_user_repository import IUserRepository


class InvalidCredentialsError(Exception):
    pass


class LoginUseCase:
    def __init__(
        self,
        user_repo: IUserRepository,
        hash_service: IHashService,
        token_service: ITokenService,
        mfa_session_service: IMfaSessionService,
    ):
        self.user_repo = user_repo
        self.hash_service = hash_service
        self.token_service = token_service
        self.mfa_session_service = mfa_session_service

    async def execute(self, request: LoginRequestDTO) -> LoginResponseDTO:
        password = request.password.get_secret_value()
        user = await self.user_repo.get_by_username(request.username)
        if not user:
            self.hash_service.verify_password(
                password, self.hash_service.get_dummy_password_hash()
            )
            raise InvalidCredentialsError("Invalid credentials")

        if not self.hash_service.verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid credentials")

        if not user.is_active():
            raise InvalidCredentialsError("Invalid credentials")

        if user.mfa_secret:
            mfa_session_id = await self.mfa_session_service.create_session(user)
            return LoginResponseDTO(
                requires_mfa=True,
                user_id=str(user.id),
                mfa_session_id=mfa_session_id,
            )

        access_token = self.token_service.create_access_token(
            AccessTokenClaims(
                subject=user.username,
                user_id=str(user.id),
                tenant_id=str(user.tenant_id),
            )
        )
        await self.user_repo.update_last_login(user.id)
        return LoginResponseDTO(
            requires_mfa=False,
            user_id=str(user.id),
            access_token=access_token,
            token_type="Bearer",
        )
