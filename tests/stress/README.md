# SGDEA Stress Testing (Locust)

Este directorio contiene la batería de pruebas de Carga y Estrés (Stress Testing) a nivel profesional usando [Locust](https://locust.io/).

## Objetivo
Validar que el DocuEngine puede soportar un volumen concurrente alto de peticiones sin incurrir en *Out Of Memory (OOM)* ni violar el límite de tamaño de subida (50MB), así como asegurar que el middleware de **SlowAPI (Rate Limiting)** funciona rechazando los ataques de *fuzzing* o DoS con código 429.

## Cómo ejecutar (Modo UI)
1. Asegúrese de tener el entorno virtual activo.
2. Ejecute:
   ```bash
   locust -f tests/stress/locustfile.py
   ```
3. Abra `http://localhost:8089` en su navegador.
4. Configure:
   - Número de usuarios: `1000`
   - Tasa de aparición: `50`
   - Host: `http://localhost:8000` (o la URL de producción).

## Cómo ejecutar (Modo Headless / CI-CD)
Para ejecutar automáticamente en una canalización (Pipeline) durante 1 minuto con 100 usuarios:
```bash
locust -f tests/stress/locustfile.py --headless -u 100 -r 20 -t 1m --host=http://localhost:8000
```
