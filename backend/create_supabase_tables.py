"""
Run this script once to create the required tables in Supabase.
"""
import asyncio
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

# Load .env from the backend directory
load_dotenv(Path(__file__).parent / ".env")

SUPABASE_DB_URL = os.environ.get("SUPABASE_DB_URL")
if not SUPABASE_DB_URL:
    raise ValueError("SUPABASE_DB_URL not set in .env")

from server import Base

async def create_tables():
    engine = create_async_engine(SUPABASE_DB_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_tables())
    print("Tables created in Supabase.")
