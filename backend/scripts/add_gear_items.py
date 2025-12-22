import os
import asyncio
from datetime import datetime, timezone
from pathlib import Path
import uuid

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient


ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / '.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')


# Gear items to add
GEAR_ITEMS = [
    {
        'name': 'Tennis Racket - Wilson Pro Staff',
        'description': 'Professional grade tennis racket with excellent control and power. Perfect for intermediate to advanced players.',
        'price_per_hour': 50,
        'stock': 8,
        'image_url': 'https://images.unsplash.com/photo-1581588667945-13abf4db4a58?w=400&h=300&fit=crop',
        'category': 'tennis'
    },
    {
        'name': 'Basketball - Spalding NBA Official',
        'description': 'Official size basketball used in NBA games. Premium composite leather construction for superior grip.',
        'price_per_hour': 30,
        'stock': 15,
        'image_url': 'https://images.unsplash.com/photo-1546519638-68e109498ffc?w=400&h=300&fit=crop',
        'category': 'basketball'
    },
    {
        'name': 'Badminton Set - Yonex Nanoray',
        'description': 'Complete badminton set with lightweight racquets and durable shuttlecocks. Ideal for casual and competitive play.',
        'price_per_hour': 40,
        'stock': 10,
        'image_url': 'https://images.unsplash.com/photo-1579504137364-ef0f3c6a7e2c?w=400&h=300&fit=crop',
        'category': 'badminton'
    },
    {
        'name': 'Football - Adidas Predator',
        'description': 'High-performance football with excellent touch and durability. Perfect for training and matches.',
        'price_per_hour': 35,
        'stock': 12,
        'image_url': 'https://images.unsplash.com/photo-1579504137364-ef0f3c6a7e2c?w=400&h=300&fit=crop',
        'category': 'football'
    },
    {
        'name': 'Cricket Bat - SS Kashmir Willow',
        'description': 'Premium cricket bat made from selected Kashmir willow. Excellent pick-up and powerful shots.',
        'price_per_hour': 60,
        'stock': 6,
        'image_url': 'https://images.unsplash.com/photo-1521205050117-aaae1fcac0d5?w=400&h=300&fit=crop',
        'category': 'cricket'
    },
    {
        'name': 'Volleyball - Mikasa MVA200',
        'description': 'Official tournament volleyball with superior grip and durability. Used in international competitions.',
        'price_per_hour': 25,
        'stock': 10,
        'image_url': 'https://images.unsplash.com/photo-1581588667945-13abf4db4a58?w=400&h=300&fit=crop',
        'category': 'volleyball'
    },
    {
        'name': 'Table Tennis Paddle - Butterfly Timo Boll',
        'description': 'Professional table tennis paddle with offensive rubber. Perfect balance of speed and spin.',
        'price_per_hour': 45,
        'stock': 8,
        'image_url': 'https://images.unsplash.com/photo-1581588667945-13abf4db4a58?w=400&h=300&fit=crop',
        'category': 'table_tennis'
    },
    {
        'name': 'Running Shoes - Nike Air Zoom',
        'description': 'Professional running shoes with responsive cushioning and breathable mesh upper. Perfect for track and road running.',
        'price_per_hour': 40,
        'stock': 12,
        'image_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=300&fit=crop',
        'category': 'shoes'
    },
    {
        'name': 'Sports Shoes - Adidas Ultraboost',
        'description': 'High-performance athletic shoes with superior comfort and energy return. Ideal for various sports activities.',
        'price_per_hour': 45,
        'stock': 10,
        'image_url': 'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=400&h=300&fit=crop',
        'category': 'shoes'
    },
    {
        'name': 'Carrom Board - Tournament Standard',
        'description': 'Professional carrom board with smooth playing surface and high-quality striker. Perfect for competitive play.',
        'price_per_hour': 25,
        'stock': 6,
        'image_url': '/images/equipment/carrom.jpg',
        'category': 'carrom'
    },
    {
        'name': 'Carrom Set - Complete with Accessories',
        'description': 'Complete carrom set including board, strikers, coins, and powder. Ideal for family and tournament play.',
        'price_per_hour': 30,
        'stock': 8,
        'image_url': '/images/equipment/carrom.jpg',
        'category': 'carrom'
    }
]


async def add_gear_items():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Add gear items
    for gear_item in GEAR_ITEMS:
        # Check if item already exists
        existing = await db.gear_items.find_one({'name': gear_item['name']})
        if not existing:
            gear_doc = {
                'id': str(uuid.uuid4()),
                'name': gear_item['name'],
                'description': gear_item['description'],
                'price_per_hour': gear_item['price_per_hour'],
                'stock': gear_item['stock'],
                'image_url': gear_item['image_url'],
                'status': 'available',
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            await db.gear_items.insert_one(gear_doc)
            print(f"Added gear item: {gear_item['name']}")
        else:
            print(f"Gear item already exists: {gear_item['name']}")
    
    client.close()


if __name__ == '__main__':
    asyncio.run(add_gear_items())