@echo off
echo =======================================================
echo     INICIANDO DOCU_ENGINE (SGDEA CERTIFICADO)
echo =======================================================
echo.
echo Activando entorno virtual...
call .venv\Scripts\activate.bat

echo.
echo Iniciando servidor FastAPI...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo.
pause
