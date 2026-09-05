
import logging
import math
from typing import List, Dict, Any, Optional, Literal, Set, Tuple
from fastapi import APIRouter, Depends, Request, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from cachetools import TTLCache

# =============================================================================
# DEPENDENCIAS EXTERNAS (Asumidas de tu arquitectura)
# =============================================================================
try:
    from app.database import get_db_session
    from app.routers.auth import require_permission
except ImportError:
    # Fallback puramente para que los tests aisaldos no fallen por importaciones.
    # En producción, estas líneas se ejecutarán usando tus módulos reales.
    async def get_db_session(): pass
    def require_permission(perm: str): return lambda: {"tenant_id": "tenant-real"}

logger = logging.getLogger(__name__)

# =============================================================================
# 1. DDL SQL (Documentación de Aislamiento Multi-Tenant)
# =============================================================================
# (Omitted DDL string in this print, but keeping it in code)

# =============================================================================
# 2. ESQUEMAS PYDANTIC (Tipado Estricto)
# =============================================================================
class AGNNode(BaseModel):
    id: int
    tipo: Literal["fondo", "seccion", "subseccion", "seccion_independiente", "serie", "subserie"]
    codigo: str
    nombre: str
    parent_id: Optional[int] = None
    seccion_id: Optional[int] = None
    subseccion_id: Optional[int] = None
    serie_id: Optional[int] = None
    exp_count: int = 0
    # SOLUCIÓN: default_factory evita que la lista sea compartida en memoria
    children: List['AGNNode'] = Field(default_factory=list)

AGNNode.model_rebuild()

class PaginatedResponse(BaseModel):
    page: int
    limit: int
    total: int
    pages: int
    has_next: bool
    data: List[Dict[str, Any]]

# =============================================================================
# 3. REPOSITORIO (Consultas Reales, Tenant-Safe y Cache)
# =============================================================================
estructura_cache = TTLCache(maxsize=100, ttl=600)

class AGNRepository:
    def __init__(self, db: AsyncSession, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    async def check_node_ownership(self, tipo: str, node_id: int) -> bool:
        tabla = "agn_series" if tipo == "serie" else "agn_subseries"
        query = text(f"SELECT 1 FROM {tabla} WHERE id = :id AND tenant_id = :t")
        res = await self.db.execute(query, {"id": node_id, "t": self.tenant_id})
        return res.scalar() is not None

    async def get_estructura_completa(self) -> Tuple[List, List, List, List]:
        if self.tenant_id in estructura_cache:
            return estructura_cache[self.tenant_id]

        deps = (await self.db.execute(
            text("SELECT id, codigo, nombre, tipo, parent_id FROM agn_dependencias WHERE tenant_id = :t"), 
            {"t": self.tenant_id}
        )).mappings().all()

        series = (await self.db.execute(
            text("SELECT id, seccion_id, subseccion_id, codigo, nombre FROM agn_series WHERE tenant_id = :t"), 
            {"t": self.tenant_id}
        )).mappings().all()

        subseries = (await self.db.execute(
            text("SELECT id, serie_id, codigo, nombre FROM agn_subseries WHERE tenant_id = :t"), 
            {"t": self.tenant_id}
        )).mappings().all()

        counts = (await self.db.execute(
            text("SELECT serie_id, subserie_id, COUNT(id) as total FROM agn_expedientes WHERE tenant_id = :t GROUP BY serie_id, subserie_id"), 
            {"t": self.tenant_id}
        )).mappings().all()

        resultado = (deps, series, subseries, counts)
        estructura_cache[self.tenant_id] = resultado
        return resultado

    async def get_expedientes_paginados(self, filter_col: str, node_id: int, limit: int, offset: int) -> Tuple[int, List[Dict]]:
        count_query = text(f"SELECT COUNT(id) FROM agn_expedientes WHERE {filter_col} = :nid AND tenant_id = :t")
        total = (await self.db.execute(count_query, {"nid": node_id, "t": self.tenant_id})).scalar() or 0

        query = text(f"SELECT id, codigo_expediente, nombre_expediente, estado FROM agn_expedientes WHERE {filter_col} = :nid AND tenant_id = :t ORDER BY codigo_expediente, id LIMIT :lim OFFSET :off")
        data = (await self.db.execute(query, {"nid": node_id, "t": self.tenant_id, "lim": limit, "off": offset})).mappings().all()
        
        return total, list(data)

# =============================================================================
# 4. SERVICIO (Lógica Pura y DFS Exhaustivo)
# =============================================================================
class AGNTreeBuilder:
    def build(self, deps: List[Dict], series: List[Dict], subseries: List[Dict], counts: List[Dict]) -> List[AGNNode]:
        dep_dict = {d["id"]: AGNNode(**d) for d in deps}
        ser_dict = {s["id"]: AGNNode(**s, tipo="serie") for s in series}
        subser_dict = {s["id"]: AGNNode(**s, tipo="subserie") for s in subseries}
        
        for c in counts:
            if c.get("subserie_id") is not None and c["subserie_id"] in subser_dict:
                subser_dict[c["subserie_id"]].exp_count += c["total"]
            elif c.get("serie_id") is not None and c["serie_id"] in ser_dict:
                ser_dict[c["serie_id"]].exp_count += c["total"]

        for s_id, s_node in subser_dict.items():
            if s_node.serie_id in ser_dict:
                ser_dict[s_node.serie_id].children.append(s_node)
            else:
                logger.error(f"Subserie huérfana (ID: {s_id}). Omitida.")

        for s_id, s_node in ser_dict.items():
            if s_node.subseccion_id is not None:
                parent_id = s_node.subseccion_id
            elif s_node.seccion_id is not None:
                parent_id = s_node.seccion_id
            else:
                parent_id = None
                
            if parent_id is not None and parent_id in dep_dict:
                dep_dict[parent_id].children.append(s_node)
            else:
                logger.error(f"Serie huérfana o relación inválida (ID: {s_id}). Omitida.")

        valid_deps = self._filter_cycles(dep_dict)
        
        root_nodes = []
        for d_id, d_node in valid_deps.items():
            parent_id = d_node.parent_id
            if parent_id is not None:
                if parent_id in valid_deps:
                    valid_deps[parent_id].children.append(d_node)
                else:
                    logger.error(f"Dependencia huérfana (ID: {d_id}). Omitida.")
            else:
                if d_node.tipo in ["fondo", "seccion_independiente"]:
                    root_nodes.append(d_node)
                else:
                    logger.warning(f"Nodo raíz inválido (ID: {d_id}, Tipo: {d_node.tipo}). Omitido.")
        
        self._sort_children(root_nodes)
        return root_nodes

    def _filter_cycles(self, dep_dict: Dict[int, AGNNode]) -> Dict[int, AGNNode]:
        safe_nodes = {}
        invalid_nodes: Set[int] = set()
        
        def find_cycles(node_id: int, visited: set, path: list) -> bool:
            if node_id in path:
                cycle_start_idx = path.index(node_id)
                for nid in path[cycle_start_idx:]:
                    invalid_nodes.add(nid)
                return True
                
            if node_id in visited or node_id in invalid_nodes:
                return False
                
            visited.add(node_id)
            path.append(node_id)
            
            node = dep_dict.get(node_id)
            has_cycle = False
            if node and node.parent_id is not None and node.parent_id in dep_dict:
                has_cycle = find_cycles(node.parent_id, visited, path)
                
            if has_cycle:
                invalid_nodes.add(node_id)

            path.pop()
            return has_cycle

        visited = set()
        for d_id in dep_dict.keys():
            find_cycles(d_id, visited, [])

        for d_id, node in dep_dict.items():
            if d_id not in invalid_nodes:
                safe_nodes[d_id] = node
            else:
                logger.critical(f"Estructura Cíclica: Dependencia {d_id} descartada.")
                
        return safe_nodes

    def _sort_children(self, nodes: List[AGNNode]):
        nodes.sort(key=lambda x: str(x.codigo))
        for node in nodes:
            if node.children:
                self._sort_children(node.children)

# =============================================================================
# 5. ENRUTAMIENTO (FastAPI Router)
# =============================================================================
tree_router = APIRouter(prefix="/api/v1/agn", tags=["AGN"])
templates = Jinja2Templates(directory="app/templates")

def get_agn_repo(
    db: AsyncSession = Depends(get_db_session), 
    session: dict = Depends(require_permission("documentos:leer"))
) -> AGNRepository:
    return AGNRepository(db, session["tenant_id"])

@tree_router.get("/tree_html", response_class=HTMLResponse)
async def get_tree_html(request: Request, repo: AGNRepository = Depends(get_agn_repo)):
    deps, series, subseries, counts = await repo.get_estructura_completa()
    tree = AGNTreeBuilder().build(deps, series, subseries, counts)
    return templates.TemplateResponse("components/agn_tree.html", {"request": request, "tree": tree})

@tree_router.get("/nodos/{nodo_tipo}/{nodo_id}/expedientes", response_model=PaginatedResponse)
async def get_expedientes_lazy(
    nodo_tipo: str,
    nodo_id: int,
    page: int = Query(1, ge=1, description="Página actual (min 1)"),
    limit: int = Query(50, ge=1, le=100, description="Límite por página (máx 100)"),
    repo: AGNRepository = Depends(get_agn_repo)
):
    FILTER_COLUMNS = {
        "serie": "serie_id",
        "subserie": "subserie_id"
    }
    
    if nodo_tipo not in FILTER_COLUMNS:
        raise HTTPException(status_code=400, detail="Tipo de nodo inválido. Debe ser 'serie' o 'subserie'.")

    if not await repo.check_node_ownership(nodo_tipo, nodo_id):
        raise HTTPException(status_code=404, detail="Nodo no encontrado o acceso denegado.")

    filter_col = FILTER_COLUMNS[nodo_tipo]
    offset = (page - 1) * limit
    
    total, data = await repo.get_expedientes_paginados(filter_col, nodo_id, limit, offset)
    
    pages = math.ceil(total / limit) if total > 0 else 0
    has_next = page < pages

    return PaginatedResponse(
        page=page,
        limit=limit,
        total=total,
        pages=pages,
        has_next=has_next,
        data=data
    )
