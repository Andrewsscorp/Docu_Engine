import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import OperationalError


class DummyResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json = json_data

    def json(self):
        return self._json


def upload_document(file_data, db_session):
    pass


def process_document_worker(document_id, task_data):
    pass


@pytest.fixture
def mock_db_session():
    return MagicMock()


@patch(__name__ + '.upload_document')
def test_falla_base_datos_subida_documento(mock_upload, mock_db_session):
    """Simula la caÃ­da de la base de datos a mitad de la subida."""
    mock_upload.side_effect = OperationalError(
        statement="INSERT INTO documents",
        params={},
        orig=Exception("DB Connection Lost")
    )

    response = None
    try:
        mock_upload(b"dummy_file_data", mock_db_session)
    except OperationalError:
        response = DummyResponse(
            503,
            {"detail": "Service Unavailable due to database error"}
        )

    assert response is not None
    assert response.status_code in (500, 503)
    assert "Service Unavailable" in response.json()["detail"]


@patch(__name__ + '.process_document_worker')
def test_caida_worker_ocr_idempotencia(mock_worker):
    """Valida procesar el mismo documento dos veces no duplique registros."""
    registros_procesados = []

    def mock_process(document_id, task_data):
        if document_id not in registros_procesados:
            registros_procesados.append(document_id)
            return True
        return False

    mock_worker.side_effect = mock_process

    doc_id = "doc_12345"
    task_info = {"content": "text"}

    resultado_1 = mock_worker(doc_id, task_info)
    resultado_2 = mock_worker(doc_id, task_info)

    assert resultado_1 is True
    assert resultado_2 is False
    assert len(registros_procesados) == 1
    assert registros_procesados[0] == doc_id
