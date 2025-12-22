import os
from dotenv import load_dotenv
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def check_admin():
    ROOT_DIR = Path('.').parent
    load_dotenv(ROOT_DIR / '.env')
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    # Check if admin user exists and their role
    admin = await db.users.find_one({'email': 'admin@college.edu'}, {'_id': 0})
    if admin:
        print(f'Admin user found: {admin}')
    else:
        print('No admin user found')
    
    # Check all users with their roles
    users = await db.users.find({}, {'_id': 0, 'password': 0}).to_list(10)
    print(f'Total users: {len(users)}')
    for user in users:
        print(f'User: {user.get("email")}, Role: {user.get("role")}, Status: {user.get("status")}')

if __name__ == "__main__":
    asyncio.run(check_admin())
