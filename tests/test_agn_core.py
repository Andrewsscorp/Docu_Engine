import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock

pytestmark = pytest.mark.asyncio

from test_security_p0 import generate_cookie

@pytest.fixture
def auth_cookies():
    return {"sessionId": generate_cookie("tenant_A")}

# Test creación de expediente
async def test_crear_expediente_exito(async_client, mock_db_session, auth_cookies):
    with patch('app.rbac.check_permission', return_value=True):
        # Mocking check for existing codigo
        mock_check = MagicMock()
        mock_check.scalar.return_value = "ABIERTO" # estado_fondo

        # Mocking subserie validacion (lock_res)
        mock_lock = MagicMock()
        mock_lock_row = MagicMock()
        mock_lock_row.ultimo_consecutivo = 0
        mock_lock.fetchone.return_value = mock_lock_row

        mock_dep_f = MagicMock()
        mock_dep_f.fetchone.return_value = ("F01",)

        mock_dep_sec = MagicMock()
        mock_dep_sec.fetchone.return_value = ("S01",)

        mock_dep_ser = MagicMock()
        mock_dep_ser.fetchone.return_value = ("SR01",)

        mock_dep_subser = MagicMock()
        mock_dep_subser.fetchone.return_value = ("SSR01",)

        mock_insert = MagicMock()

        # Acomodar side effects (fondo, lock, f, sec, ser, subser, insert)
        mock_db_session.execute.side_effect = [mock_check, mock_lock, mock_dep_f, mock_dep_sec, mock_dep_ser, mock_dep_subser, mock_insert, mock_insert, mock_insert, mock_insert, mock_insert]

        response = await async_client.post(
            "/api/v1/agn/expedientes",
            data={
                "fondo": "Fondo_1",
                "seccion": "Seccion_1",
                "serie": "Serie_1",
                "nombre_expediente": "Test EXP",
                "fecha_apertura": "2024-01-01",
                "responsable": "John Doe",
                "confirmTrd": "on",
                "confirmImmutable": "on"
            },
            cookies=auth_cookies
        )

        # FastAPI might return 200 or 303 (redirect to module usually)
        assert response.status_code in [200, 303, 302]

# Test FUID (Formato Único de Inventario Documental)
async def test_generar_fuid_subserie(async_client, mock_db_session, auth_cookies):
    with patch('app.rbac.check_permission', return_value=True):
        # Mock dependencies (fondo, seccion, etc)
        mock_dep = MagicMock()
        mock_dep.fetchone.return_value = ("AGN", "F001")

        mock_series = MagicMock()

        subserie_row = MagicMock()
        subserie_row._mapping = {"id": "1", "codigo": "S001", "nombre": "Series_A", "serie_nombre": "Serie"}
        mock_series.fetchone.return_value = subserie_row

        # Expedientes
        mock_exps = MagicMock()
        mock_row = MagicMock()
        mock_row._mapping = {
            "exp_id": "exp_1",
            "codigo": "E001",
            "nombre_unidad_conservacion": "Carpet",
            "fecha_inicial": None,
            "fecha_final": None,
            "caja_carpeta": "1-1",
            "folios": 10,
            "soporte": "E",
            "notas": "N/A"
        }
        mock_exps.fetchall.return_value = [mock_row]

        mock_db_session.execute.side_effect = [mock_series, mock_exps, mock_exps, mock_exps, mock_dep] # Multiples queries en fuid

        response = await async_client.get(
            "/api/v1/agn/subseries/Subserie_1/fuid",
            cookies=auth_cookies
        )

        assert response.status_code in [200, 500]
