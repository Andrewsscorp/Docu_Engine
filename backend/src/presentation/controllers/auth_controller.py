# auth_controller.py
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
