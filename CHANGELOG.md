# Registro de Cambios (Changelog)

Todos los cambios notables de este proyecto se documentarán en este archivo.

## [1.1.0] - 2026-08-22
### Añadido
- **Sistema de Desplazamiento Táctil:** Se implementó deslizamiento con el ratón (Drag-to-Scroll) en el carrusel de documentos recientes usando Alpine.js.
- **Botones de Navegación del Carrusel:** Los botones `<` y `>` ahora desplazan el carrusel mediante JavaScript nativo de forma fluida.
- **Extracción de Texto Segura:** Se mejoró el cálculo SHA-256 en el cliente para validación temprana de duplicados.

### Arreglado
- **Colisión de Interfaz de HTMX:** Se resolvió un problema crítico de "bucle de carga infinita" migrando el renderizado del carrusel de `hx-swap="outerHTML"` a `hx-swap="innerHTML"`.
- **Ventana de Detalles Modal:** Se corrigió un error en el que la propagación de eventos impedía la apertura del modal al hacer clic en los documentos.
- **CSP (Content Security Policy):** Se eliminaron referencias bloqueadas de imágenes de Wikimedia, siendo reemplazadas por avatares generados por interfaz.

## [1.0.0] - Lanzamiento Inicial
### Añadido
- Arquitectura central con FastAPI y base de datos asíncrona (PostgreSQL).
- Autenticación segura y motor de roles y grupos.
- Tablero principal interactivo (Dashboard) y zona segura de carga de documentos (Upload Zone).
- Buscador completo (FTS) para indexación de archivos procesados por OCR.
