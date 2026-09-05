import pytest
from uuid import UUID, uuid4

from backend.src.domain.entities.usuario import EstadoUsuario, Usuario


@pytest.fixture
def base_user_data():
    return {
        "id": uuid4(),
        "username": "usuario_test",
        "password_hash": "hash_super_seguro_de_60_caracteres",
        "estado": EstadoUsuario.ACTIVO,
        "tenant_id": uuid4(),
        "mfa_secret": "secreto_totp_valido",
        "es_cuenta_servicio": False,
    }


def test_creacion_usuario_valido(base_user_data):
    user = Usuario(**base_user_data)

    assert user.username == "usuario_test"
    assert user.estado == EstadoUsuario.ACTIVO


def test_coercion_de_tipos(base_user_data):
    datos_string = base_user_data.copy()
    datos_string["id"] = str(datos_string["id"])
    datos_string["tenant_id"] = str(datos_string["tenant_id"])
    datos_string["estado"] = "INACTIVO"

    user = Usuario(**datos_string)

    assert isinstance(user.id, UUID)
    assert isinstance(user.tenant_id, UUID)
    assert isinstance(user.estado, EstadoUsuario)
    assert user.estado == EstadoUsuario.INACTIVO


def test_repr_oculta_credenciales(base_user_data):
    user = Usuario(**base_user_data)
    representacion = repr(user)

    assert "password_hash" not in representacion
    assert "mfa_secret" not in representacion
    assert base_user_data["password_hash"] not in representacion
    assert "username" in representacion


@pytest.mark.parametrize(
    ("estado", "expected"),
    [
        (EstadoUsuario.ACTIVO, True),
        (EstadoUsuario.INACTIVO, False),
        (EstadoUsuario.BLOQUEADO, False),
    ],
)
def test_is_active(base_user_data, estado, expected):
    base_user_data["estado"] = estado

    assert Usuario(**base_user_data).is_active() is expected


def test_error_uuid_invalido(base_user_data):
    base_user_data["id"] = "no-es-un-uuid"

    with pytest.raises(ValueError, match="Usuario contiene un UUID o estado inválido"):
        Usuario(**base_user_data)


def test_error_estado_invalido(base_user_data):
    base_user_data["estado"] = "ESTADO_INVENTADO"

    with pytest.raises(ValueError, match="Usuario contiene un UUID o estado inválido"):
        Usuario(**base_user_data)


@pytest.mark.parametrize("bad_username", ["", "a" * 255, 12345, None])
def test_error_username_invalido(base_user_data, bad_username):
    base_user_data["username"] = bad_username

    with pytest.raises(ValueError, match="username debe tener entre 1 y 254"):
        Usuario(**base_user_data)


@pytest.mark.parametrize("bad_hash", ["a" * 256, 12345])
def test_error_password_hash_invalido(base_user_data, bad_hash):
    base_user_data["password_hash"] = bad_hash

    with pytest.raises(ValueError, match="password_hash inválido o demasiado largo"):
        Usuario(**base_user_data)


@pytest.mark.parametrize("bad_mfa", ["a" * 129, 123])
def test_error_mfa_invalido(base_user_data, bad_mfa):
    base_user_data["mfa_secret"] = bad_mfa

    with pytest.raises(ValueError, match="mfa_secret no puede superar 128"):
        Usuario(**base_user_data)


def test_error_es_cuenta_servicio_invalida(base_user_data):
    base_user_data["es_cuenta_servicio"] = "False"

    with pytest.raises(ValueError, match="es_cuenta_servicio debe ser un booleano"):
        Usuario(**base_user_data)
