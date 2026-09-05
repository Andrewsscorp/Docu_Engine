# auth_dtos.py
import re
from typing import Literal, Optional

from pydantic import BaseModel, Field, SecretStr, field_validator, model_validator

class LoginRequestDTO(BaseModel):
    username: str = Field(min_length=3, max_length=254)
    password: SecretStr = Field(min_length=8, max_length=128)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if value != value.strip():
            raise ValueError("username cannot start or end with whitespace")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value().strip():
            raise ValueError("password cannot be blank")
        return value

class LoginResponseDTO(BaseModel):
    requires_mfa: bool
    user_id: str
    access_token: Optional[str] = None
    token_type: Optional[Literal["Bearer"]] = None
    mfa_session_id: Optional[str] = None

    @model_validator(mode="after")
    def validate_authentication_state(self):
        if self.requires_mfa:
            if self.access_token is not None or self.token_type is not None:
                raise ValueError("MFA responses cannot contain an access token")
            if not self.mfa_session_id:
                raise ValueError("MFA responses require an MFA session")
        else:
            if self.access_token is None or self.token_type != "Bearer":
                raise ValueError("Successful responses require a Bearer access token")
            if self.mfa_session_id is not None:
                raise ValueError("Access token responses cannot contain an MFA session")
        return self


class MfaVerificationRequestDTO(BaseModel):
    mfa_session_id: str = Field(min_length=43, max_length=128)
    otp_code: SecretStr

    @field_validator("otp_code")
    @classmethod
    def validate_otp_code(cls, value: SecretStr) -> SecretStr:
        if not re.fullmatch(r"\d{6}", value.get_secret_value()):
            raise ValueError("otp_code must contain exactly 6 digits")
        return value
