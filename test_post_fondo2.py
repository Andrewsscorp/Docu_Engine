import asyncio
import httpx

async def main():
    async with httpx.AsyncClient(base_url='http://localhost:8000') as client:
        # First, login
        resp = await client.post('/api/v1/auth/login', data={'username': 'admin', 'password': 'admin_password'})
        print("Login status:", resp.status_code)
        
        # Then, create a fondo
        data = {
            'codigo': 'F-TEST',
            'nombre': 'Test Fondo',
            'acto_administrativo': 'Decreto 123',
            'estado': 'ABIERTO'
        }
        resp = await client.post('/api/v1/agn/fondos', data=data)
        print("Create fondo status:", resp.status_code)
        print("Response:", resp.text)

if __name__ == '__main__':
    asyncio.run(main())
