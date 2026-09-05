# auth_dtos.py
from pydantic import BaseModel

class LoginRequestDTO(BaseModel):
    username: str
    password: str

class LoginResponseDTO(BaseModel):
    token: str
    requires_mfa: bool
    user_id: str
