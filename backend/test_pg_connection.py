import asyncio
import os
from dotenv import load_dotenv
import asyncpg

load_dotenv(".env")
url = os.environ.get("SUPABASE_DB_URL")
# Convert SQLAlchemy asyncpg URL to raw asyncpg connection params
db_url = url.replace("postgresql+asyncpg://", "")

async def test():
    try:
        conn = await asyncpg.connect(db_url)
        print("Connected to Supabase!")
        version = await conn.fetchval("SELECT version()")
        print("Postgres version:", version)
        await conn.close()
    except Exception as e:
        print("Connection failed:", e)

asyncio.run(test())
