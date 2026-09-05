import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.main import app
import json

async def run():
    engine = create_async_engine("postgresql+asyncpg://docuengine_api:api_secure_password_123@localhost:5432/docuengine")
    
    inventory = {"tables": [], "endpoints": []}
    
    # Get Tables
    async with engine.begin() as conn:
        res = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        for row in res:
            inventory["tables"].append(row[0])
            
    # Get Endpoints
    for route in app.routes:
        methods = ",".join(route.methods) if hasattr(route, 'methods') else "WS"
        path = route.path
        inventory["endpoints"].append(f"{methods} {path}")
        
    with open("inventory_baseline.json", "w") as f:
        json.dump(inventory, f, indent=2)

asyncio.run(run())
