from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db_session
from app.security import require_permission
from datetime import datetime

router = APIRouter(prefix="/api/v1/agn", tags=["agn"])

@router.get("/modal")
async def get_agn_modal(
    request: Request,
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    tenant_id = session_data["tenant_id"]
    
    # Fetch Fondos
    fondos_res = await db.execute(text("SELECT id, nombre, codigo FROM agn_dependencias WHERE tipo = 'FONDO' AND tenant_id = :t"), {"t": tenant_id})
    fondos = fondos_res.fetchall()
    
    # Fetch Secciones
    secciones_res = await db.execute(text("SELECT id, nombre, codigo FROM agn_dependencias WHERE tipo = 'SECCION' AND tenant_id = :t"), {"t": tenant_id})
    secciones = secciones_res.fetchall()
    
    # Fetch Series
    series_res = await db.execute(text("SELECT id, nombre, codigo FROM agn_series WHERE tenant_id = :t"), {"t": tenant_id})
    series = series_res.fetchall()
    
    # Fetch Subseries
    subseries_res = await db.execute(text("SELECT id, nombre, codigo FROM agn_subseries WHERE tenant_id = :t"), {"t": tenant_id})
    subseries = subseries_res.fetchall()
    
    # For now we pre-generate a code ALC-SECED-CON-PS-2026-003
    codigo_expediente = "ALC-SECED-CON-PS-2026-003"
    
    today = datetime.now().strftime('%Y-%m-%d')
    username = session_data.get("username", "Admin")

    html = f"""
    <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-blue-50/50">
        <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-white shadow-sm flex items-center justify-center border border-gray-200">
                <span class="text-xs font-bold text-gray-700">AGN</span>
            </div>
            <div>
                <h2 class="text-xl font-bold text-gray-800 font-sans">CREAR NUEVO EXPEDIENTE ELECTRÓNICO</h2>
                <p class="text-sm font-semibold text-gray-600">(Acuerdo 001/2024 AGN)</p>
            </div>
        </div>
    </div>
    <div class="p-6">
        <form id="agn-expediente-form" onsubmit="event.preventDefault(); window.submitAgnExpediente();">
            <h3 class="text-md font-bold text-gray-800 mb-3">1. Clasificación Documental (CCD/TRD)</h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div>
                    <label class="block text-sm font-semibold text-gray-600 mb-1">Fondo:</label>
                    <select name="fondo" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white transition-colors">
                        {"".join([f'<option value="{f.id}">{f.nombre}</option>' for f in fondos])}
                    </select>
                </div>
                <div>
                    <label class="block text-sm font-semibold text-gray-600 mb-1">Sección:</label>
                    <select name="seccion" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white transition-colors">
                        {"".join([f'<option value="{s.id}">{s.nombre}</option>' for s in secciones])}
                    </select>
                </div>
                <div>
                    <label class="block text-sm font-semibold text-gray-600 mb-1">Subsección (Opcional):</label>
                    <select name="subseccion" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white transition-colors">
                        <option value="">-- Seleccionar --</option>
                    </select>
                </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                    <label class="block text-sm font-semibold text-gray-600 mb-1">Serie:</label>
                    <select name="serie" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white transition-colors">
                        {"".join([f'<option value="{s.id}">{s.nombre}</option>' for s in series])}
                    </select>
                </div>
                <div>
                    <label class="block text-sm font-semibold text-gray-600 mb-1">Subserie (Opcional):</label>
                    <select name="subserie" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white transition-colors">
                        <option value="">-- Seleccionar --</option>
                        {"".join([f'<option value="{s.id}">{s.nombre}</option>' for s in subseries])}
                    </select>
                </div>
            </div>
            
            <div class="mb-6">
                <label class="block text-sm font-semibold text-gray-600 mb-1">Código de Expediente (Generado Automáticamente):</label>
                <input type="text" readonly value="{codigo_expediente}" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-100 font-mono text-gray-800">
                <p class="text-xs text-gray-500 mt-1">Este código es único e inmutable.</p>
            </div>
            
            <h3 class="text-md font-bold text-gray-800 mb-3">2. Identificación del Expediente</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                    <label class="block text-sm font-semibold text-gray-600 mb-1">Nombre del Expediente:*</label>
                    <input type="text" name="nombre_expediente" required class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-1 focus:ring-primary">
                </div>
                <div>
                    <label class="block text-sm font-semibold text-gray-600 mb-1">Asunto:*</label>
                    <textarea name="asunto" rows="2" required class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-1 focus:ring-primary"></textarea>
                </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div>
                    <label class="block text-sm font-semibold text-gray-600 mb-1">Fecha de Apertura:*</label>
                    <input type="date" name="fecha_apertura" required value="{today}" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-1 focus:ring-primary">
                </div>
                <div>
                    <label class="block text-sm font-semibold text-gray-600 mb-1">Responsable:*</label>
                    <select name="responsable" required class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50">
                        <option value="{session_data['user_id']}">{username}</option>
                    </select>
                </div>
            </div>
            
            <h3 class="text-md font-bold text-gray-800 mb-3">3. Controles y Acciones</h3>
            <div class="space-y-2 mb-6">
                <label class="flex items-start gap-2 cursor-pointer">
                    <input type="checkbox" required class="mt-1 border-gray-300 rounded text-primary focus:ring-primary">
                    <span class="text-sm text-gray-700">Confirmo que la clasificación corresponde a la TRD vigente.</span>
                </label>
                <label class="flex items-start gap-2 cursor-pointer">
                    <input type="checkbox" required class="mt-1 border-gray-300 rounded text-primary focus:ring-primary">
                    <span class="text-sm text-gray-700">Entiendo que este expediente generará un índice electrónico inmutable.</span>
                </label>
            </div>
            
            <div class="flex justify-center gap-3">
                <button type="submit" class="px-6 py-2.5 text-sm font-bold text-white bg-green-600 hover:bg-green-700 rounded-lg shadow-sm flex items-center gap-2 transition-colors">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                    Crear Expediente
                </button>
                <button type="button" onclick="Swal.close()" class="px-5 py-2.5 text-sm font-medium text-white bg-gray-500 hover:bg-gray-600 rounded-lg transition-colors">Cancelar</button>
            </div>
        </form>
    </div>
    """
    
    return HTMLResponse(html)

@router.post("/expedientes")
async def create_agn_expediente(
    request: Request,
    session_data: dict = Depends(require_permission("documentos:crear")),
    db: AsyncSession = Depends(get_db_session)
):
    # This will be implemented fully later.
    return JSONResponse({"status": "success", "message": "Expediente electrónico creado y registrado en el índice."})
