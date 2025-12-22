import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def test_pending_rentals():
    try:
        # Connect to MongoDB
        mongo_url = os.environ['MONGO_URL']
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.environ['DB_NAME']]
        
        # Count pending rentals
        count = await db.gear_rentals.count_documents({'status': 'pending'})
        print(f'Pending rentals: {count}')
        
        # Get the actual pending rentals
        pending_rentals = await db.gear_rentals.find(
            {'status': 'pending'},
            {'_id': 0}
        ).to_list(100)
        
        print(f"Pending rentals data: {pending_rentals}")
        
        if pending_rentals:
            # Show associated user and gear info
            for rental in pending_rentals:
                user = await db.users.find_one({'id': rental['user_id']}, {'_id': 0, 'password': 0})
                gear = await db.gear_items.find_one({'id': rental['gear_id']}, {'_id': 0})
                print(f"Rental {rental['id']}:")
                print(f"  User: {user['name'] if user else 'Unknown'}")
                print(f"  Gear: {gear['name'] if gear else 'Unknown'}")
                print(f"  Quantity: {rental['quantity']}")
        
        await client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_pending_rentals())