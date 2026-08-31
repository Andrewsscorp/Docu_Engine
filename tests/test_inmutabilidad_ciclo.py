import pytest

class EstadoExpedienteError(Exception):
    pass

class AppendOnlyError(Exception):
    pass

class Expediente:
    def __init__(self, id, estado="Abierto"):
        self.id = id
        self.estado = estado

    def cerrar(self):
        self.estado = "Cerrado"

    def editar(self, nuevos_datos):
        if self.estado == "Cerrado":
            raise EstadoExpedienteError("No se puede editar un expediente cerrado.")
        # LÃ³gica de ediciÃ³n
        pass

class Auditoria:
    def __init__(self):
        self._eventos = []

    def registrar_evento(self, evento):
        self._eventos.append(evento)

    def obtener_eventos(self):
        return tuple(self._eventos) # Retornamos tupla para simular inmutabilidad

    def eliminar_evento(self, evento_id):
        raise AppendOnlyError("La tabla de auditorÃ­a es Append-Only, no se pueden eliminar eventos.")
        
    def modificar_evento(self, evento_id, nuevos_datos):
        raise AppendOnlyError("La tabla de auditorÃ­a es Append-Only, no se pueden modificar eventos.")


def test_REC_EXP_001_inmutabilidad_expediente_cerrado():
    """
    Caso REC-EXP-001: Que intentar editar a la fuerza un expediente que ya fue "Cerrado" 
    genere un rechazo o excepciÃ³n (Demuestra la inmutabilidad).
    """
    expediente = Expediente(id="EXP-2023-001")
    expediente.cerrar()
    
    with pytest.raises(EstadoExpedienteError, match="No se puede editar un expediente cerrado."):
        expediente.editar({"campo": "nuevo valor"})


def test_AUD_001_auditoria_append_only():
    """
    Caso AUD-001: Que intentar modificar o borrar eventos de la tabla de auditorÃ­a 
    (emulando DELETE o manipulaciÃ³n manual del objeto de auditorÃ­a) lance una excepciÃ³n, 
    validando el diseÃ±o Append-Only.
    """
    auditoria = Auditoria()
    auditoria.registrar_evento({"id": 1, "accion": "CREACION"})
    
    with pytest.raises(AppendOnlyError, match="Append-Only"):
        auditoria.eliminar_evento(1)
        
    with pytest.raises(AppendOnlyError, match="Append-Only"):
        auditoria.modificar_evento(1, {"accion": "MODIFICACION"})
