from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from app.database import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.services.novu_client import novu_client

router = APIRouter(prefix="/api/v1/notificaciones", tags=["Notificaciones"])

@router.get("/conteo", response_class=HTMLResponse)
async def get_unread_count(request: Request):
    """
    Endpoint HTMX para polling silencioso.
    Devuelve un span con el número si hay notificaciones, o vacío si no hay.
    """
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        return HTMLResponse(content="")
        
    count = await novu_client.get_unread_count(user_id)
    
    if count > 0:
        return HTMLResponse(content=f'<span class="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">{count}</span>')
    return HTMLResponse(content="")

@router.get("/recientes", response_class=HTMLResponse)
async def get_recent_notifications(request: Request):
    """
    Devuelve las tarjetas HTML de las notificaciones recientes para inyectar en el dropdown.
    """
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        return HTMLResponse(content='<div class="p-4 text-center text-gray-500 text-sm">No autenticado</div>')
        
    response_data = await novu_client.get_recent_notifications(user_id)
    notificaciones = response_data.get("data", [])
    
    if not notificaciones:
        return HTMLResponse(content='''
        <div class="p-8 text-center text-gray-500 flex flex-col items-center">
            <svg class="w-12 h-12 text-gray-200 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path></svg>
            <p class="text-sm">No tienes notificaciones pendientes</p>
        </div>
        ''')
    
    # En un caso real, renderizaríamos notification_card.html usando Jinja2.
    # Por ahora, construiremos el HTML aquí o delegaremos a plantillas si tenemos request.app.state.templates
    
    # Para ser estrictos, si DocuEngine usa templates globales:
    templates = getattr(request.app.state, "templates", None)
    if templates:
        return templates.TemplateResponse(
            "components/notification_inbox.html", 
            {"request": request, "notificaciones": notificaciones}
        )
        
    return HTMLResponse(content="<div>Notificaciones Cargadas (Requiere setup de plantillas)</div>")

@router.post("/preferencias")
async def update_preferences(request: Request):
    """
    Endpoint dummy para recibir las actualizaciones de toggles.
    En un entorno real, esto llamaría a novu_client.update_preferences(...)
    """
    form = await request.form()
    evento = form.get("evento")
    canal = form.get("canal")
    # Simula el delay de red
    import asyncio
    await asyncio.sleep(0.2)
    return HTMLResponse(status_code=200)
