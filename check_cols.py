import asyncio
import asyncpg

async def main():
    conn = await asyncpg.connect(user="postgres", password="superuser", database="docuengine", host="127.0.0.1")
    rows = await conn.fetch("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'agn_expedientes';")
    for r in rows:
        print(f"{r['column_name']}: {r['data_type']}")
    await conn.close()

asyncio.run(main())
