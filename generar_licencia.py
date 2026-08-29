#!/usr/bin/env python3
"""
Generador de Licencias Off-Grid — DocuEngine
==============================================
- Se auto-instala las dependencias que falten (rich, python-dotenv).
- Genera tokens firmados con HMAC-SHA256 (misma lógica criptográfica que siempre).
- Soporta varios tipos de licencia, duración configurable (días/meses/años),
  ID único de licencia, y guarda un registro local de todas las licencias emitidas.
"""

import sys
import subprocess
import importlib

# ---------------------------------------------------------------------------
# 1) AUTO-INSTALACIÓN DE DEPENDENCIAS
#    Si falta alguna librería, se instala sola con pip y se relanza el script.
# ---------------------------------------------------------------------------
REQUIRED_PACKAGES = {
    "rich": "rich",
    "dotenv": "python-dotenv",
    "pyperclip": "pyperclip",
}


def _bootstrap_dependencies():
    faltantes = []
    for module_name, pip_name in REQUIRED_PACKAGES.items():
        try:
            importlib.import_module(module_name)
        except ImportError:
            faltantes.append(pip_name)

    if not faltantes:
        return  # todo instalado, seguimos normal

    print(f"[setup] Instalando dependencias faltantes: {', '.join(faltantes)} ...")
    pip_cmd = [sys.executable, "-m", "pip", "install", "--quiet", *faltantes]

    # Intento normal primero
    result = subprocess.run(pip_cmd, capture_output=True, text=True)

    # Si falla por PEP 668 (entornos gestionados por el sistema), reintenta con --break-system-packages
    if result.returncode != 0:
        result = subprocess.run(
            pip_cmd + ["--break-system-packages"], capture_output=True, text=True
        )

    if result.returncode != 0:
        print("[setup] No se pudieron instalar las dependencias automáticamente.")
        print(result.stderr)
        print(f"\nInstálalas manualmente con:\n    pip install {' '.join(faltantes)} --break-system-packages\n")
        sys.exit(1)

    print("[setup] Dependencias instaladas correctamente. Reiniciando script...\n")
    # Relanzamos el propio script como proceso nuevo para que los imports ya funcionen
    os_execv_args = [sys.executable] + sys.argv
    import os
    os.execv(sys.executable, os_execv_args)


_bootstrap_dependencies()

# ---------------------------------------------------------------------------
# A partir de aquí, todas las dependencias ya existen garantizado
# ---------------------------------------------------------------------------
import hmac
import hashlib
import json
import base64
import os
import time
import uuid
from datetime import datetime, timedelta

from dotenv import load_dotenv
import pyperclip
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich.text import Text
from rich.align import Align
from rich.rule import Rule
from rich.status import Status
from rich import box

console = Console()

# ---------------------------------------------------------------------------
# 2) CONFIGURACIÓN Y CLAVE MAESTRA
# ---------------------------------------------------------------------------
load_dotenv()
_hmac_env = os.environ.get("MASTER_HMAC_KEY")

if not _hmac_env:
    console.print()
    console.print(
        Panel.fit(
            "[bold white]MASTER_HMAC_KEY no encontrada en el entorno.[/bold white]\n"
            "Ejecuta [bold cyan]configurar_entorno.py[/bold cyan] primero, o define la\n"
            "variable en tu archivo [bold cyan].env[/bold cyan].",
            title="[bold red]✖ ERROR CRÍTICO[/bold red]",
            border_style="red",
            box=box.HEAVY,
            padding=(1, 3),
        )
    )
    raise RuntimeError("CRÍTICO: MASTER_HMAC_KEY no encontrada en entorno. Ejecute configurar_entorno.py primero.")

MASTER_HMAC_KEY = _hmac_env.encode("utf-8")

LICENSE_LOG_PATH = "licencias_emitidas.json"

# Tipos de licencia soportados: nombre -> (rol interno, color de acento, descripción)
LICENSE_TYPES = {
    "1": ("admin", "bold red", "Administrador — acceso total al sistema"),
    "2": ("standard", "bold cyan", "Estándar — uso normal del producto"),
    "3": ("trial", "bold yellow", "Prueba — funciones limitadas / tiempo corto"),
    "4": ("enterprise", "bold magenta", "Empresarial — multi-usuario / soporte prioritario"),
}

# Unidades de tiempo soportadas para la duración
TIME_UNITS = {
    "1": ("días", 1),
    "2": ("meses", 30),
    "3": ("años", 365),
}


# ---------------------------------------------------------------------------
# 3) LÓGICA DE NEGOCIO (núcleo criptográfico, sin cambios de fondo)
# ---------------------------------------------------------------------------
def generate_license(hwid_hash: str, rol: str = "admin", days_valid: int = 30, max_activations: int = 1, notes: str = ""):
    issued_at = datetime.now()
    exp_date = issued_at + timedelta(days=days_valid)
    license_id = str(uuid.uuid4())

    payload = {
        "license_id": license_id,
        "rol": rol,
        "hwid_hash": hwid_hash,
        "issued_at": issued_at.isoformat(),
        "exp_timestamp": exp_date.timestamp(),
        "max_activations": max_activations,
        "notes": notes,
    }

    # Serializar y codificar en Base64 URL-safe (sin padding para estética)
    payload_json = json.dumps(payload, sort_keys=True).encode("utf-8")
    b64_payload = base64.urlsafe_b64encode(payload_json).decode("utf-8").rstrip("=")

    # Firmar el payload original con HMAC-SHA256
    signature = hmac.new(MASTER_HMAC_KEY, payload_json, hashlib.sha256).hexdigest()

    token = f"{b64_payload}.{signature}"
    return token, payload, exp_date


def copiar_al_portapapeles(token: str) -> bool:
    """Copia el token al portapapeles del sistema. Devuelve True si tuvo éxito."""
    try:
        pyperclip.copy(token)
        # Verificación: releemos el portapapeles para confirmar que quedó bien
        return pyperclip.paste() == token
    except Exception:
        return False


def guardar_en_registro(token: str, payload: dict):
    """Guarda un historial local de licencias emitidas (append-only)."""
    registro = []
    if os.path.exists(LICENSE_LOG_PATH):
        try:
            with open(LICENSE_LOG_PATH, "r", encoding="utf-8") as f:
                registro = json.load(f)
        except (json.JSONDecodeError, OSError):
            registro = []

    registro.append({**payload, "token": token, "generado_en": datetime.now().isoformat()})

    with open(LICENSE_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(registro, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# 4) INTERFAZ VISUAL / MENÚS
# ---------------------------------------------------------------------------
def print_banner():
    banner = Text(justify="center")
    banner.append("╔═══════════════════════════════════════════╗\n", style="bold cyan")
    banner.append("║ ", style="bold cyan")
    banner.append("GENERADOR DE LICENCIAS OFF-GRID", style="bold white on dark_cyan")
    banner.append("      ║\n", style="bold cyan")
    banner.append("║              ", style="bold cyan")
    banner.append("DocuEngine · Módulo Admin", style="italic bright_cyan")
    banner.append("            ║\n", style="bold cyan")
    banner.append("╚═══════════════════════════════════════════╝", style="bold cyan")
    console.print(Align.center(banner))
    console.print()


def ask_hwid() -> str:
    console.print(Rule("[bold yellow]Paso 1 · Cliente[/bold yellow]", style="yellow"))
    hwid = Prompt.ask(
        "[bold]HWID Hash del cliente objetivo[/bold] [dim](ej. b7f8a9c3e1d2...)[/dim]",
        default="",
        show_default=False,
    )
    if not hwid:
        hwid = "hash_simulado_123"
        console.print(f"[yellow]⚠ No se introdujo HWID. Usando valor por defecto:[/yellow] [bold]{hwid}[/bold]")
    console.print()
    return hwid


def ask_license_type() -> tuple[str, str]:
    console.print(Rule("[bold yellow]Paso 2 · Tipo de licencia[/bold yellow]", style="yellow"))

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold white")
    table.add_column("#", width=3)
    table.add_column("Tipo")
    table.add_column("Descripción")
    for key, (rol, color, desc) in LICENSE_TYPES.items():
        table.add_row(key, f"[{color}]{rol}[/{color}]", desc)
    console.print(table)

    choice = Prompt.ask(
        "[bold]Selecciona el tipo de licencia[/bold]",
        choices=list(LICENSE_TYPES.keys()),
        default="2",
    )
    rol, color, _ = LICENSE_TYPES[choice]
    console.print()
    return rol, color


def ask_duration() -> int:
    console.print(Rule("[bold yellow]Paso 3 · Duración[/bold yellow]", style="yellow"))

    table = Table(box=box.SIMPLE, show_header=False)
    for key, (label, _) in TIME_UNITS.items():
        table.add_row(f"[cyan]{key}[/cyan]", label)
    console.print(table)

    unidad_choice = Prompt.ask(
        "[bold]Unidad de tiempo[/bold]",
        choices=list(TIME_UNITS.keys()),
        default="1",
    )
    unidad_label, multiplicador = TIME_UNITS[unidad_choice]

    cantidad = IntPrompt.ask(f"[bold]Cantidad de {unidad_label}[/bold]", default=30 if unidad_choice == "1" else 1)

    dias_totales = cantidad * multiplicador
    console.print(f"[dim]→ Duración total: {cantidad} {unidad_label} = {dias_totales} días[/dim]")
    console.print()
    return dias_totales


def ask_extra_options() -> tuple[int, str]:
    console.print(Rule("[bold yellow]Paso 4 · Opciones adicionales[/bold yellow]", style="yellow"))
    max_activations = IntPrompt.ask("[bold]Máximo de activaciones / dispositivos[/bold]", default=1)
    notes = Prompt.ask("[bold]Notas u observaciones[/bold] [dim](opcional)[/dim]", default="", show_default=False)
    console.print()
    return max_activations, notes


def render_result(token: str, payload: dict, exp_date: datetime, color: str):
    with Status("[bold cyan]Firmando payload con HMAC-SHA256...[/bold cyan]", spinner="dots"):
        time.sleep(0.6)

    console.print(
        Panel.fit(
            "[bold green]✔ Licencia generada exitosamente[/bold green]",
            border_style="green",
            box=box.ROUNDED,
        )
    )

    table = Table(title="Detalles de la licencia", box=box.SIMPLE_HEAVY, header_style="bold white")
    table.add_column("Campo", style="cyan", no_wrap=True)
    table.add_column("Valor", style="white")

    table.add_row("ID de licencia", payload["license_id"])
    table.add_row("Tipo / Rol", f"[{color}]{payload['rol']}[/{color}]")
    table.add_row("HWID Hash", payload["hwid_hash"])
    table.add_row("Emitida", payload["issued_at"])
    table.add_row("Expira", exp_date.strftime("%Y-%m-%d %H:%M:%S"))
    table.add_row("Máx. activaciones", str(payload["max_activations"]))
    table.add_row("Notas", payload["notes"] or "—")
    table.add_row("Algoritmo", "HMAC-SHA256")

    console.print(table)
    console.print()

    console.print(
        Panel(
            Text(token, style="bold bright_green", overflow="fold"),
            title="[bold white]TOKEN DE LICENCIA[/bold white]",
            subtitle="[dim]cópialo tal cual, sin espacios[/dim]",
            border_style="bright_green",
            box=box.DOUBLE,
            padding=(1, 2),
        )
    )

    console.print()

    copiado = copiar_al_portapapeles(token)
    if copiado:
        console.print("[bold green]📋 Token copiado al portapapeles automáticamente.[/bold green] Solo pega con Ctrl+V.")
    else:
        console.print(
            "[bold yellow]⚠ No se pudo copiar automáticamente al portapapeles[/bold yellow] "
            "(puede pasar en entornos sin acceso al portapapeles del sistema, ej. WSL/SSH sin xclip). "
            "Copia el token manualmente desde el panel de arriba."
        )

    console.print(f"[dim]➤ Registro guardado en [bold]{LICENSE_LOG_PATH}[/bold][/dim]")
    console.print("[dim]➤ Entrégale el token al cliente para su registro local.[/dim]")
    console.print()


# ---------------------------------------------------------------------------
# 5) FLUJO PRINCIPAL
# ---------------------------------------------------------------------------
def main():
    console.clear()
    print_banner()

    hwid = ask_hwid()
    rol, color = ask_license_type()
    dias_totales = ask_duration()
    max_activations, notes = ask_extra_options()

    console.print()
    token, payload, exp_date = generate_license(
        hwid_hash=hwid,
        rol=rol,
        days_valid=dias_totales,
        max_activations=max_activations,
        notes=notes,
    )

    guardar_en_registro(token, payload)
    render_result(token, payload, exp_date, color)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]✖ Operación cancelada por el usuario.[/bold red]")
        sys.exit(1)