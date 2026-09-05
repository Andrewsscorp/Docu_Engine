with open(".env", "w", encoding="utf-8") as f:
    f.write("SECRET_KEY=dummy-secret-key-for-development\n")
    f.write("DATABASE_URL=postgresql+asyncpg://docuengine_api:api_secure_password_123@localhost:5432/docuengine\n")
    f.write("MASTER_HMAC_KEY=12345678901234567890123456789012\n")
    f.write("DB_CRYPT_KEY=12345678901234567890123456789012\n")

with open(".env.example", "w", encoding="utf-8") as f:
    f.write("SECRET_KEY=generate-a-secure-random-key-here\n")
    f.write("DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname\n")
    f.write("MASTER_HMAC_KEY=32-byte-hmac-key-here\n")
    f.write("DB_CRYPT_KEY=32-byte-crypt-key-here\n")

# Make sure main.py loads dotenv
with open("app/main.py", "r", encoding="utf-8") as f:
    content = f.read()

if "from dotenv import load_dotenv" in content and "load_dotenv()" not in content:
    content = content.replace("from dotenv import load_dotenv", "from dotenv import load_dotenv\nload_dotenv()")
    with open("app/main.py", "w", encoding="utf-8") as f:
        f.write(content)

