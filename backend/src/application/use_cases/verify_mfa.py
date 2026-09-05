from backend.src.application.dtos.auth_dtos import (
    LoginResponseDTO,
    MfaVerificationRequestDTO,
)
from backend.src.domain.interfaces.i_mfa_session_service import IMfaSessionService
from backend.src.domain.interfaces.i_security_services import (
    AccessTokenClaims,
    ITokenService,
)
from backend.src.domain.interfaces.i_user_repository import IUserRepository


class VerifyMfaUseCase:
    def __init__(
        self,
        mfa_session_service: IMfaSessionService,
        token_service: ITokenService,
        user_repo: IUserRepository,
    ):
        self.mfa_session_service = mfa_session_service
        self.token_service = token_service
        self.user_repo = user_repo

    async def execute(self, request: MfaVerificationRequestDTO) -> LoginResponseDTO:
        session = await self.mfa_session_service.verify_and_consume(
            request.mfa_session_id, request.otp_code.get_secret_value()
        )
        access_token = self.token_service.create_access_token(
            AccessTokenClaims(
                subject=session.username,
                user_id=str(session.user_id),
                tenant_id=str(session.tenant_id),
            )
        )
        await self.user_repo.update_last_login(session.user_id)
        return LoginResponseDTO(
            requires_mfa=False,
            user_id=str(session.user_id),
            access_token=access_token,
            token_type="Bearer",
        )
