import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os

DB_HOST = os.getenv('DB_HOST', 'localhost')
# Assuming standard postgres password for local dev
DATABASE_URL = f'postgresql+asyncpg://postgres:123456@{DB_HOST}:5432/docuengine'

engine = create_async_engine(DATABASE_URL)

statements = [
    '''
    CREATE TABLE folders (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        tenant_id UUID NOT NULL REFERENCES tenants(id),
        name VARCHAR(255) NOT NULL,
        color VARCHAR(20) DEFAULT '#000000',
        created_by UUID REFERENCES users(id),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    )
    ''',
    '''ALTER TABLE documents ADD COLUMN folder_id UUID REFERENCES folders(id)''',
    '''
    CREATE TABLE folder_audit_logs (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        folder_id UUID REFERENCES folders(id) ON DELETE CASCADE,
        action VARCHAR(50) NOT NULL,
        user_id UUID REFERENCES users(id),
        details JSONB,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    )
    ''',
    '''CREATE INDEX idx_folders_tenant ON folders(tenant_id)''',
    '''CREATE INDEX idx_documents_folder ON documents(folder_id)''',
    '''CREATE INDEX idx_folder_audit_folder ON folder_audit_logs(folder_id)''',
    '''GRANT ALL PRIVILEGES ON TABLE folders TO docuengine_api''',
    '''GRANT ALL PRIVILEGES ON TABLE folder_audit_logs TO docuengine_api'''
]

async def run_migration():
    async with engine.begin() as conn:
        for sql in statements:
            try:
                await conn.execute(text(sql))
            except Exception as e:
                print(f"Skipped/Error on {sql[:20].strip()}: {e}")
        print("Migration executed successfully.")

asyncio.run(run_migration())
