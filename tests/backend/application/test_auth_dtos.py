import pytest
from pydantic import SecretStr, ValidationError

from backend.src.application.dtos.auth_dtos import (
    LoginRequestDTO,
    LoginResponseDTO,
    MfaVerificationRequestDTO,
)


def test_login_request_masks_password():
    request = LoginRequestDTO(username="user", password="correct-password")

    assert isinstance(request.password, SecretStr)
    assert request.password.get_secret_value() == "correct-password"
    assert "correct-password" not in repr(request)
    assert "correct-password" not in request.model_dump_json()


@pytest.mark.parametrize("password", ["", "x" * 129])
def test_login_request_rejects_invalid_password_length(password):
    with pytest.raises(ValidationError):
        LoginRequestDTO(username="user", password=password)


@pytest.mark.parametrize("username", ["ab", "   ", " user"])
def test_login_request_rejects_weak_username(username):
    with pytest.raises(ValidationError):
        LoginRequestDTO(username=username, password="correct-password")


def test_login_response_uses_oauth_fields():
    response = LoginResponseDTO(
        requires_mfa=False,
        user_id="user-1",
        access_token="signed-token",
        token_type="Bearer",
    )

    assert response.access_token == "signed-token"
    assert response.token_type == "Bearer"
    assert response.mfa_session_id is None


def test_login_response_rejects_access_token_with_mfa():
    with pytest.raises(ValidationError, match="cannot contain an access token"):
        LoginResponseDTO(
            requires_mfa=True,
            user_id="user-1",
            access_token="signed-token",
            token_type="Bearer",
            mfa_session_id="a" * 43,
        )


def test_login_response_requires_mfa_session():
    with pytest.raises(ValidationError, match="require an MFA session"):
        LoginResponseDTO(requires_mfa=True, user_id="user-1")


def test_mfa_request_masks_otp():
    request = MfaVerificationRequestDTO(
        mfa_session_id="a" * 43,
        otp_code="123456",
    )

    assert isinstance(request.otp_code, SecretStr)
    assert request.otp_code.get_secret_value() == "123456"
    assert "123456" not in repr(request)
    assert "123456" not in request.model_dump_json()
