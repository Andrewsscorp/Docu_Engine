# Pruebas End-to-End (E2E) con Playwright

Este directorio contiene las pruebas de interfaz de usuario de **DocuEngine** automatizadas mediante [Playwright](https://playwright.dev/python/). 

## Requisitos Previos

Dado que Playwright necesita descargar navegadores emulados (Chromium, Firefox, WebKit), el administrador o el pipeline CI/CD debe ejecutar lo siguiente antes de correr las pruebas:

```bash
# Descargar binarios de navegadores (Solo se hace una vez)
playwright install chromium
```

## Ejecutar las pruebas

La aplicación FastAPI **debe estar ejecutándose** en el puerto 8000 en otra terminal para que Playwright pueda navegar por ella:

```bash
pytest tests/e2e/test_dashboard_ui.py --base-url=http://localhost:8000 -v
```

Si deseas ver el navegador abriéndose gráficamente y haciendo los clics (útil para depurar), agrega la bandera `--headed`:

```bash
pytest tests/e2e/test_dashboard_ui.py --base-url=http://localhost:8000 --headed -v
```
