# auth_controller.py
from fastapi import HTTPException
from backend.src.application.dtos.auth_dtos import (
    LoginRequestDTO,
    LoginResponseDTO,
    MfaVerificationRequestDTO,
)
from backend.src.domain.interfaces.i_mfa_session_service import MfaSessionInvalidError
from backend.src.application.use_cases.login_user import (
    InvalidCredentialsError,
    LoginUseCase,
)
from backend.src.application.use_cases.verify_mfa import VerifyMfaUseCase

class AuthController:
    def __init__(self, login_use_case: LoginUseCase, verify_mfa_use_case: VerifyMfaUseCase):
        self.login_use_case = login_use_case
        self.verify_mfa_use_case = verify_mfa_use_case

    async def login(self, request: LoginRequestDTO) -> LoginResponseDTO:
        try:
            return await self.login_use_case.execute(request)
        except InvalidCredentialsError:
            raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

    async def verify_mfa(self, request: MfaVerificationRequestDTO) -> LoginResponseDTO:
        try:
            return await self.verify_mfa_use_case.execute(request)
        except MfaSessionInvalidError:
            raise HTTPException(status_code=401, detail="Invalid MFA session or code")
