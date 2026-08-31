import pytest
from unittest.mock import AsyncMock, patch
from fastapi import Request
from app.routers.agn import delete_expediente_tipologia

@pytest.mark.asyncio
async def test_tenant_isolation_delete_trd_rule():
    """
    Verifica que el borrado de reglas TRD incluya obligatoriamente el filtro de tenant_id.
    Simula al Inquilino A intentando borrar una regla TRD y analiza la sentencia SQL generada.
    """
    mock_db = AsyncMock()
    mock_request = AsyncMock(spec=Request)
    
    # Simular sesion del Inquilino A
    fake_session = {
        "tenant_id": "tenant_A_123",
        "user_id": "user_123",
        "permissions": ["documentos:crear"]
    }
    
    # Ejecutar la ruta directamente (omitiendo middlewares)
    try:
        # get_control_tipologias_view expects mock returns, we expect it to fail or just mock it out
        with patch('app.routers.agn.get_control_tipologias_view', new_callable=AsyncMock) as mock_view:
            mock_view.return_value = {"status": "success"}
            await delete_expediente_tipologia("exp_B_999", "tipo_555", mock_request, fake_session, mock_db)
    except Exception:
        pass # Ignorar fallos secundarios en dependencias, nos importa la consulta de borrado
        
    # Verificar que db.execute fue llamado
    assert mock_db.execute.called, "db.execute no fue invocado"
    
    # Extraer la consulta SQL enviada a SQLAlchemy
    # call_args[0][0] is the text() object
    call_args = mock_db.execute.call_args
    sql_text_obj = call_args[0][0]
    sql_string = str(sql_text_obj.text).upper()
    
    # Extraer parametros enviados
    sql_params = call_args[0][1]
    
    # Validaciones Criticas P0:
    assert "DELETE FROM AGN_EXPEDIENTE_TIPOLOGIA" in sql_string
    assert "TENANT_ID = :T" in sql_string, "VULNERABILIDAD: La consulta no filtra por tenant_id"
    assert sql_params["t"] == "tenant_A_123", "VULNERABILIDAD: El tenant inyectado no coincide con el de la sesion"

