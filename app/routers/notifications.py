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

from fastapi import Query
from datetime import datetime, timedelta

@router.get("/buzon", response_class=HTMLResponse)
async def buscar_buzon(
    request: Request,
    q: str = Query(""),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Endpoint de HTMX para el Buzón de Revisiones.
    En una implementación real, este endpoint buscaría en la tabla 	areas_asignaciones.
    """
    user_id = getattr(request.state, "user_id", None)
    
    # Empty State (Ejemplo si buscamos algo que no existe)
    if q and q.lower() == "vacio":
        return HTMLResponse("""
        <div class="flex flex-col items-center justify-center h-full py-16">
            <div class="w-32 h-32 bg-slate-100 rounded-full flex items-center justify-center mb-6">
                <svg class="w-16 h-16 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 13l4 4L19 7"></path>
                </svg>
            </div>
            <h3 class="text-xl text-slate-600 font-medium mb-1">Estás al día</h3>
            <p class="text-sm text-slate-400">No tienes documentos pendientes por revisar. Tómate un café.</p>
        </div>
        """)

    now = datetime.utcnow()
    # Mock Cards
    cards = [
        {
            "id": "1",
            "doc_id": "doc-uuid-1",
            "remitente": "Andrés Suárez",
            "titulo": "Auditoría Financiera - Contrato 045",
            "tiempo_asignado": "Hace 2 horas",
            "etiqueta_texto": "Revisión Urgente",
            "etiqueta_color": "bg-blue-50 text-blue-700",
            "deadline": (now + timedelta(hours=4)).strftime("%Y-%m-%dT%H:%M:%SZ") # Amarillo
        },
        {
            "id": "2",
            "doc_id": "doc-uuid-2",
            "remitente": "Carlos V",
            "titulo": "Liquidación de Nómina - Mayo",
            "tiempo_asignado": "Hace 1 hora",
            "etiqueta_texto": "Firma Requerida",
            "etiqueta_color": "bg-purple-50 text-purple-700",
            "deadline": (now + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ") # Verde
        },
        {
            "id": "3",
            "doc_id": "doc-uuid-3",
            "remitente": "",
            "titulo": "Resolución DIAN 003",
            "tiempo_asignado": "Hace 5 horas",
            "etiqueta_texto": "Revisión Urgente",
            "etiqueta_color": "bg-red-50 text-red-700",
            "deadline": (now - timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ") # Rojo (Vencido)
        }
    ]

    html_out = ""
    for c in cards:
        initials = "".join([n[0] for n in c['remitente'].split()]) if c['remitente'] else "AS"
        avatar_html = f"""
        <div class="w-10 h-10 rounded-full bg-indigo-100 text-indigo-700 font-bold flex items-center justify-center shrink-0">
            {initials}
        </div>
        """ if c['remitente'] else """
        <div class="w-10 h-10 rounded-full bg-slate-200 text-slate-500 font-bold flex items-center justify-center shrink-0">
            AS
        </div>
        """
        
        card_html = f"""
        <div class="bg-white rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow duration-200 cursor-pointer border border-slate-100 w-full"
             hx-get="/api/v1/documentos/{c['doc_id']}/drawer" 
             hx-target="#drawer-content" 
             hx-swap="innerHTML"
             @click="currentDocId = '{c['doc_id']}'; drawerAbierto = true">
             
            <div class="flex items-start gap-4">
                <!-- Bloque Izquierdo: Avatar -->
                {avatar_html}
                
                <!-- Bloque Central: Datos -->
                <div class="flex-1 min-w-0">
                    <h3 class="text-lg font-semibold text-slate-900 truncate">{c['titulo']}</h3>
                    <p class="text-sm text-slate-500 mb-2">Asignado por {c['remitente'] or 'Sistema'} • {c['tiempo_asignado']}</p>
                    
                    <div>
                        <span class="rounded-full px-2.5 py-0.5 text-xs font-medium {c['etiqueta_color']}">
                            {c['etiqueta_texto']}
                        </span>
                    </div>
                </div>
                
                <!-- Bloque Derecho: SLA Semáforo con Alpine.js -->
                <div class="flex flex-col items-end shrink-0" 
                     x-data="{{
                        deadline: new Date('{c['deadline']}').getTime(),
                        now: Date.now(),
                        init() {{
                            setInterval(() => this.now = Date.now(), 60000);
                        }},
                        get diffHours() {{
                            return (this.deadline - this.now) / (1000 * 60 * 60);
                        }},
                        get state() {{
                            if (this.diffHours < 0) return 'red';
                            if (this.diffHours <= 24) return 'amber';
                            return 'green';
                        }}
                     }}">
                     
                     <!-- Renderizado Condicional Alpine -->
                     <template x-if="state === 'green'">
                        <div class="text-slate-500 text-sm font-medium flex items-center gap-1">
                            <span>Vence en</span>
                            <span x-text="Math.floor(diffHours/24) + ' días'"></span>
                        </div>
                     </template>
                     
                     <template x-if="state === 'amber'">
                        <div class="bg-amber-100 text-amber-800 px-3 py-1.5 rounded-lg text-sm font-bold flex items-center gap-1">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                            <span>Vence en <span x-text="Math.floor(diffHours) + ' horas'"></span></span>
                        </div>
                     </template>
                     
                     <template x-if="state === 'red'">
                        <div class="text-red-600 font-bold text-sm flex items-center gap-1 animate-pulse">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                            <span>Vencido</span>
                        </div>
                     </template>
                </div>
            </div>
        </div>
        """
        html_out += card_html
        
    return HTMLResponse(content=html_out)
