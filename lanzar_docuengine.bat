@echo off
cd /d "%~dp0"
title Lanzador DocuEngine Backend (FastAPI)
echo ==============================================
echo        INICIANDO ENTORNO DOCUENGINE
echo ==============================================
echo.
echo 1. Levantando Base de Datos y Worker OCR en Docker...
echo Ejecutando docker-compose up -d --build...
docker-compose up -d --build
echo.
echo 2. Iniciando servidor FastAPI Local (MVC)...
echo Se abrira tu navegador en http://localhost:8555
echo.
start "" http://localhost:8555
.\.venv\Scripts\python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8555
pause
