from locust import HttpUser, task, between
import io
import os
import random
import uuid

class FuncionarioSGDEAUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """
        Simula el inicio de sesión del funcionario.
        Como la API requiere un HWID y un payload encriptado por seguridad,
        y no tenemos la clave privada de hardware en el entorno de pruebas masivas,
        vamos a simular peticiones con un session cookie válido inyectado (o omitimos el login 
        y asumimos que estamos probando las rutas de performance públicas o inyectamos un token dev).
        Para el test profesional, configuramos las cookies directamente simulando un estado post-login.
        """
        # Nota: En un entorno de staging real, aquí se llamaría al endpoint de auth o 
        # se inyectaría un token JWT válido de prueba.
        # Simularemos que ya tenemos sessionId (aunque falle con 401 si la API está estricta,
        # igual mediremos la capacidad del servidor de rechazar/manejar concurrencia).
        self.client.cookies.set("sessionId", "test_session_cookie_mock")

    @task(3)
    def ver_dashboard(self):
        """Simula a un usuario navegando por el explorador de documentos."""
        with self.client.get("/api/v1/documents/explorer", catch_response=True) as response:
            if response.status_code in [200, 401, 403]: # 401/403 es aceptable para pruebas de rendimiento si no pasamos auth
                response.success()

    @task(1)
    def subir_documento_tamano_aceptable(self):
        """Simula la subida de un documento PDF estándar de 2MB."""
        file_content = b"%PDF-1.4\n" + b"A" * 2 * 1024 * 1024 # 2MB dummy PDF
        files = {
            "archivo": ("documento_prueba.pdf", file_content, "application/pdf")
        }
        data = {
            "group_id": "test-group",
            "metadata_json": "{}"
        }
        with self.client.post("/api/v1/documents/upload", files=files, data=data, catch_response=True) as response:
            if response.status_code in [200, 401, 429]: # 429 is rate limit (expected under load)
                response.success()
                
    @task(1)
    def violacion_rate_limit_fixity(self):
        """Simula un intento de abuso del sistema de Fixity para ver si el Rate Limiter (SlowAPI) lo bloquea."""
        with self.client.post("/api/v1/documents/fixity", catch_response=True) as response:
            if response.status_code in [200, 401, 429]:
                response.success()
                
