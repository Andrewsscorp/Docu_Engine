import os

files_to_fix = ["app/security.py", "app/main.py"]
for filepath in files_to_fix:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace hardcoded secret
    content = content.replace(
        'SECRET_KEY = "dummy-secret-key-for-development"', 
        'import os\nSECRET_KEY = os.environ.get("SECRET_KEY")\nif not SECRET_KEY:\n    raise ValueError("Missing SECRET_KEY environment variable")'
    )
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

with open("app/database.py", "r", encoding="utf-8") as f:
    content = f.read()
    content = content.replace(
        'DATABASE_URL = f"postgresql+asyncpg://docuengine_api:api_secure_password_123@{DB_HOST}:5432/docuengine"',
        'DATABASE_URL = os.environ.get("DATABASE_URL")\nif not DATABASE_URL:\n    raise ValueError("Missing DATABASE_URL environment variable")'
    )
    with open("app/database.py", "w", encoding="utf-8") as f:
        f.write(content)

with open(".env", "w", encoding="utf-8") as f:
    f.write("SECRET_KEY=dummy-secret-key-for-development\n")
    f.write("DATABASE_URL=postgresql+asyncpg://docuengine_api:api_secure_password_123@localhost:5432/docuengine\n")

with open(".env.example", "w", encoding="utf-8") as f:
    f.write("SECRET_KEY=generate-a-secure-random-key-here\n")
    f.write("DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname\n")

print("Secrets removed and moved to .env!")
