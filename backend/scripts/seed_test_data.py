import os
import asyncio
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import bcrypt


ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / '.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')


async def seed():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    # Admin user
    admin_email = 'admin@college.edu'
    admin_password_plain = 'admin123'

    existing_admin = await db.users.find_one({'email': admin_email})
    if not existing_admin:
        admin_id = os.urandom(16).hex()
        admin_password_hashed = bcrypt.hashpw(
            admin_password_plain.encode('utf-8'),
            bcrypt.gensalt(),
        ).decode('utf-8')

        admin_doc = {
            'id': admin_id,
            'name': 'Admin',
            'email': admin_email,
            'phone': '1234567890',
            'password': admin_password_hashed,
            'role': 'admin',
            'status': 'approved',
            'created_at': datetime.now(timezone.utc).isoformat(),
        }
        await db.users.insert_one(admin_doc)
        print(f"Created admin user: {admin_email} / {admin_password_plain}")
    else:
        print(f"Admin already exists: {admin_email}")

    # Student user
    student_email = 'student@college.edu'
    student_password_plain = 'student123'

    existing_student = await db.users.find_one({'email': student_email})
    if not existing_student:
        student_id = os.urandom(16).hex()
        student_password_hashed = bcrypt.hashpw(
            student_password_plain.encode('utf-8'),
            bcrypt.gensalt(),
        ).decode('utf-8')

        student_doc = {
            'id': student_id,
            'name': 'Test Student',
            'email': student_email,
            'phone': '9876543210',
            'password': student_password_hashed,
            'role': 'student',
            'status': 'approved',
            'created_at': datetime.now(timezone.utc).isoformat(),
        }
        await db.users.insert_one(student_doc)
        print(f"Created student user: {student_email} / {student_password_plain}")
    else:
        print(f"Student already exists: {student_email}")

    client.close()


if __name__ == '__main__':
    asyncio.run(seed())
