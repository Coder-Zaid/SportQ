import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")

# Get the Supabase URL from environment variables
url = os.environ.get("SUPABASE_DB_URL")
print(f"Attempting to connect to: {url}")

# Convert SQLAlchemy asyncpg URL to raw asyncpg connection params
if url:
    # Try different URL formats
    db_url = url.replace("postgresql+asyncpg://", "postgresql://")
    print(f"Trying with URL: {db_url}")
else:
    print("SUPABASE_DB_URL not found in .env")
    exit(1)

async def test_connection():
    try:
        print("Testing connection...")
        conn = await asyncpg.connect(db_url, timeout=10)
        print("✅ Successfully connected to Supabase!")
        version = await conn.fetchval("SELECT version()")
        print(f"PostgreSQL version: {version}")
        await conn.close()
        print("Connection closed.")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        
        # Try alternative connection method
        print("\nTrying alternative connection method...")
        try:
            # Parse the URL manually
            import urllib.parse
            parsed = urllib.parse.urlparse(url.replace("postgresql+asyncpg://", "postgresql://"))
            conn = await asyncpg.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                user=parsed.username,
                password=parsed.password,
                database=parsed.path[1:],  # Remove leading slash
                timeout=10
            )
            print("✅ Successfully connected to Supabase with alternative method!")
            version = await conn.fetchval("SELECT version()")
            print(f"PostgreSQL version: {version}")
            await conn.close()
            print("Connection closed.")
        except Exception as e2:
            print(f"❌ Alternative connection also failed: {e2}")

if __name__ == "__main__":
    asyncio.run(test_connection())