@echo off
cd /d "%~dp0"
title Lanzador DocuEngine Backend (FastAPI)
echo ==============================================
echo        INICIANDO ENTORNO DOCUENGINE
echo ==============================================
echo.
echo 1. Calculando capacidad del servidor (25%% de los hilos para OCR)...
for /f %%i in ('powershell -command "[math]::Max(1, [math]::Floor((Get-CimInstance Win32_Processor | Measure-Object -Property NumberOfLogicalProcessors -Sum).Sum * 0.25))"') do set TARGET_WORKERS=%%i
echo Asignando %TARGET_WORKERS% trabajadores OCR en paralelo.
echo.
echo 2. Levantando Base de Datos y Workers OCR en Docker...
echo Ejecutando docker-compose up -d --build --scale ocr_worker=%TARGET_WORKERS%...
docker-compose up -d --build --scale ocr_worker=%TARGET_WORKERS%
echo.
echo 3. Iniciando servidor FastAPI Local (MVC)...
echo Se abrira tu navegador en http://localhost:8555
echo.
start "" http://localhost:8555
.\.venv\Scripts\python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8555
pause
