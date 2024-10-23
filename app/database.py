from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings
import asyncio

# Global connection pool
_client = None
_db = None

async def init_db():
    global _client, _db
    if _client is None:
        # Configure connection pool
        _client = AsyncIOMotorClient(
            settings.mongodb_url,
            maxPoolSize=50,
            minPoolSize=10,
            maxIdleTimeMS=50000,
            waitQueueTimeoutMS=5000
        )
        _db = _client[settings.database_name]
    return _db

async def get_database():
    if _db is None:
        await init_db()
    return _db

async def create_indexes(db):
    # Create compound indexes for common queries
    await db.allocations.create_index([
        ("vehicle_id", 1),
        ("allocation_date", 1)
    ], unique=True)
    
    await db.allocations.create_index([
        ("employee_id", 1),
        ("allocation_date", 1)
    ])
    
    # Compound index for history queries
    await db.allocations.create_index([
        ("employee_id", 1),
        ("vehicle_id", 1),
        ("allocation_date", 1)
    ])