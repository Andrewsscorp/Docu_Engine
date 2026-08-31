@echo off
echo =======================================================
echo     INICIANDO DOCU_ENGINE (SGDEA CERTIFICADO)
echo =======================================================
echo.
echo Activando entorno virtual...
call .venv\Scripts\activate.bat

echo.
echo Abriendo navegador en 3 segundos...
start /b cmd /c "ping localhost -n 4 > nul && start http://localhost:8000"

echo Iniciando servidor FastAPI...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo.
pause
