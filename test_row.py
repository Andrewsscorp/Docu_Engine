import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi import Request
from app.routers.etiquetas import list_etiquetas

async def test():
    engine = create_async_engine('postgresql+asyncpg://docuengine_api:api_password@localhost/docuengine_db')
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
    
    async with TestingSessionLocal() as db:
        class DummyRequest:
            pass
        req = DummyRequest()
        req.state = DummyRequest()
        req.state.user_id = 'test'
        
        try:
            resp = await list_etiquetas(req, 'Todos', None, db)
            print(resp.body.decode('utf-8'))
        except Exception as e:
            print("Error:", e)

asyncio.run(test())
