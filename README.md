# DocuEngine 🚀

¡Bienvenido a **DocuEngine**! Un sistema de gestión documental moderno, rápido y seguro, diseñado para entornos empresariales. Combina un potente backend asíncrono con una interfaz de usuario reactiva y ultraligera.

<img src="https://ui-avatars.com/api/?name=Docu+Engine&background=4318FF&color=fff&rounded=true&size=256" align="right" />

## 🌟 Características Principales

- **Bóveda Documental Segura:** Almacenamiento centralizado con aislamiento por Inquilinos (Multi-Tenant).
- **Procesamiento OCR Integrado:** Extracción automática de texto de imágenes y PDFs escaneados usando Tesseract OCR, ejecutado en trabajadores en segundo plano (Celery/RabbitMQ).
- **Buscador de Texto Completo (FTS):** Motor de búsqueda ultra-rápido basado en PostgreSQL FTS (Full Text Search) para encontrar documentos por su contenido o título instantáneamente.
- **Roles y Permisos (RBAC):** Sistema de control de acceso granular (Administradores, Gestores, Usuarios) basado en JWT y cookies seguras (`HttpOnly`).
- **Interfaz Reactiva sin Frameworks Pesados:** Frontend construido puramente con **HTMX**, **Alpine.js** y **Tailwind CSS**. Sin tiempos de carga, SPA real.
- **Prevención de Duplicados:** Cálculo de hashes (SHA-256) en el cliente para bloquear archivos duplicados antes de que consuman ancho de banda.
- **Arquitectura Escalable:** Desarrollado con **FastAPI** (Python) y **SQLAlchemy Async**.

## 🛠️ Stack Tecnológico

*   **Backend:** Python 3.10+, FastAPI, SQLAlchemy (asyncpg), Celery
*   **Base de Datos:** PostgreSQL 15+ (con soporte para GIN Indexing y TSVector)
*   **Frontend:** HTMX, Alpine.js (v3), Tailwind CSS
*   **Mensajería:** RabbitMQ (para colas de tareas OCR)
*   **Despliegue:** Docker, Docker Compose

## 🚀 Guía de Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Andrewsscorp/Docu_Engine.git
   cd Docu_Engine
   ```

2. **Configurar las variables de entorno:**
   Copia el archivo de ejemplo y configura tus credenciales de base de datos (¡Nunca subas tu `.env` al repo!):
   ```bash
   cp .env.example .env
   ```

3. **Despliegue rápido con Docker:**
   ```bash
   docker-compose up -d --build
   ```

   *La aplicación estará disponible en `http://localhost:8555`*

## 📁 Estructura del Proyecto

*   `/app/routers/` - Controladores y rutas (API y vistas de HTMX).
*   `/app/templates/` - Plantillas Jinja2 (Páginas y componentes modulares).
*   `/app/database.py` - Configuración asíncrona de SQLAlchemy.
*   `/ocr_worker.py` - Trabajador encargado de la extracción de texto.

## 📄 Licencia

Este proyecto es propiedad de **Andrewsscorp**. Queda estrictamente prohibida su distribución sin una licencia comercial válida emitida por el autor.
