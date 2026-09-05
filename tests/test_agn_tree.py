
import math
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.routers.agn_tree import tree_router, get_agn_repo, AGNRepository, AGNTreeBuilder, AGNNode

app = FastAPI()
app.include_router(tree_router)

class MockRepo(AGNRepository):
    def __init__(self, tenant_id):
        super().__init__(None, tenant_id)
    async def check_node_ownership(self, tipo, node_id): return node_id == 1
    async def get_expedientes_paginados(self, f, n, l, o): return 1284, [{"id": 1, "codigo_expediente": "A"}]

def override_repo():
    return MockRepo("tenant-test")

app.dependency_overrides[get_agn_repo] = override_repo
client = TestClient(app)

@pytest.fixture
def builder():
    return AGNTreeBuilder()

def test_pydantic_type_validation():
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        AGNNode(id=1, tipo="inventado", codigo="X", nombre="X")
    n1 = AGNNode(id=1, tipo="fondo", codigo="A", nombre="A")
    n2 = AGNNode(id=2, tipo="fondo", codigo="B", nombre="B")
    n1.children.append(n2)
    assert len(n1.children) == 1
    assert len(n2.children) == 0

def test_dfs_cycle_A_B_C_A(builder, caplog):
    deps = [
        {"id": 1, "tipo": "seccion", "codigo": "A", "nombre": "A", "parent_id": 3},
        {"id": 2, "tipo": "seccion", "codigo": "B", "nombre": "B", "parent_id": 1},
        {"id": 3, "tipo": "seccion", "codigo": "C", "nombre": "C", "parent_id": 2}
    ]
    tree = builder.build(deps, [], [], [])
    assert len(tree) == 0
    assert "Estructura Cíclica: Dependencia 1" in caplog.text

def test_dfs_cycle_A_B_C_D_A(builder, caplog):
    deps = [
        {"id": 1, "tipo": "seccion", "codigo": "A", "nombre": "A", "parent_id": 4},
        {"id": 2, "tipo": "seccion", "codigo": "B", "nombre": "B", "parent_id": 1},
        {"id": 3, "tipo": "seccion", "codigo": "C", "nombre": "C", "parent_id": 2},
        {"id": 4, "tipo": "seccion", "codigo": "D", "nombre": "D", "parent_id": 3}
    ]
    tree = builder.build(deps, [], [], [])
    assert len(tree) == 0

def test_orphan_handling_explicit(builder, caplog):
    series = [{"id": 1, "seccion_id": 99, "codigo": "S1", "nombre": "S1", "subseccion_id": None}]
    subseries = [{"id": 1, "serie_id": 88, "codigo": "SS1", "nombre": "SS1"}]
    tree = builder.build([], series, subseries, [])
    assert len(tree) == 0
    assert "Serie huérfana o relación inválida" in caplog.text
    assert "Subserie huérfana" in caplog.text

def test_api_pagination_metadata_and_limits():
    resp = client.get("/api/v1/agn/nodos/serie/1/expedientes?limit=101")
    assert resp.status_code == 422 
    
    resp = client.get("/api/v1/agn/nodos/serie/1/expedientes?page=0")
    assert resp.status_code == 422 
    
    resp = client.get("/api/v1/agn/nodos/invalido/1/expedientes")
    assert resp.status_code == 400
    assert "Tipo de nodo inválido" in resp.json()["detail"]

    resp = client.get("/api/v1/agn/nodos/serie/1/expedientes?page=2&limit=50")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1284
    assert data["pages"] == math.ceil(1284/50)
    assert data["has_next"] is True
    assert len(data["data"]) == 1

def test_cross_tenant_prevention():
    resp = client.get("/api/v1/agn/nodos/serie/999/expedientes")
    assert resp.status_code == 404
    assert "Nodo no encontrado o acceso denegado" in resp.json()["detail"]
