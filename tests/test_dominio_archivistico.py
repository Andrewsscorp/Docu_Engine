import pytest

class EstadoExpediente:
    BORRADOR = "Borrador"
    ABIERTO = "Abierto"
    CERRADO = "Cerrado"

class ExpedienteError(Exception):
    pass

class Expediente:
    def __init__(self, trd):
        self.trd = trd
        self.estado = EstadoExpediente.BORRADOR
        self.documentos = []
        self.folios = set()

    def agregar_documento(self, tipologia):
        self.documentos.append(tipologia)

    def agregar_folio(self, folio_id):
        if folio_id in self.folios:
            raise ValueError("Folio duplicado no permitido en el mismo expediente.")
        self.folios.add(folio_id)

    def abrir(self):
        if self.estado != EstadoExpediente.BORRADOR:
            raise ExpedienteError("TransiciÃ³n invÃ¡lida: Solo se puede abrir un expediente en Borrador.")
        self.estado = EstadoExpediente.ABIERTO

    def cerrar(self):
        if self.estado != EstadoExpediente.ABIERTO:
            raise ExpedienteError("TransiciÃ³n invÃ¡lida: Solo se puede cerrar un expediente Abierto.")
        
        # Verificar TRD (TipologÃ­as obligatorias)
        tipologias_presentes = set(self.documentos)
        for tipologia, es_obligatoria in self.trd.items():
            if es_obligatoria and tipologia not in tipologias_presentes:
                raise ExpedienteError(f"No se puede cerrar: falta la tipologÃ­a obligatoria '{tipologia}'.")
        
        self.estado = EstadoExpediente.CERRADO


# 1. Que un expediente no pueda cerrarse si faltan tipologÃ­as documentales marcadas como 'obligatorias' en la TRD.
def test_cierre_falla_por_tipologia_obligatoria_faltante():
    trd = {"Acta": True, "Resolucion": False}
    expediente = Expediente(trd)
    expediente.abrir()
    
    with pytest.raises(ExpedienteError, match="No se puede cerrar: falta la tipologÃ­a obligatoria 'Acta'."):
        expediente.cerrar()

def test_cierre_exitoso_con_tipologias_obligatorias():
    trd = {"Acta": True, "Resolucion": False}
    expediente = Expediente(trd)
    expediente.abrir()
    expediente.agregar_documento("Acta")
    expediente.cerrar()
    
    assert expediente.estado == EstadoExpediente.CERRADO

# 2. Que no se pueda tener folios duplicados en el mismo expediente.
def test_folios_duplicados_no_permitidos():
    trd = {}
    expediente = Expediente(trd)
    expediente.agregar_folio("F-001")
    
    with pytest.raises(ValueError, match="Folio duplicado no permitido en el mismo expediente."):
        expediente.agregar_folio("F-001")

# 3. Que la transiciÃ³n de estados sea estricta (Borrador -> Abierto -> Cerrado).
def test_transicion_estado_estricta():
    trd = {}
    expediente = Expediente(trd)
    
    assert expediente.estado == EstadoExpediente.BORRADOR
    
    # No se puede cerrar directamente desde Borrador
    with pytest.raises(ExpedienteError, match="TransiciÃ³n invÃ¡lida: Solo se puede cerrar un expediente Abierto."):
        expediente.cerrar()
        
    expediente.abrir()
    assert expediente.estado == EstadoExpediente.ABIERTO
    
    # No se puede volver a abrir
    with pytest.raises(ExpedienteError, match="TransiciÃ³n invÃ¡lida: Solo se puede abrir un expediente en Borrador."):
        expediente.abrir()
        
    expediente.cerrar()
    assert expediente.estado == EstadoExpediente.CERRADO
    
    # No se puede cerrar de nuevo
    with pytest.raises(ExpedienteError, match="TransiciÃ³n invÃ¡lida: Solo se puede cerrar un expediente Abierto."):
        expediente.cerrar()
