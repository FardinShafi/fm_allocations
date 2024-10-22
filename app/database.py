from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

async def get_database():
    client = AsyncIOMotorClient(settings.mongodb_url)
    return client[settings.database_name]

async def create_indexes(db):
    await db.allocations.create_index([
        ("vehicle_id", 1),
        ("allocation_date", 1)
    ], unique=True)
    await db.allocations.create_index("employee_id")
    await db.allocations.create_index("allocation_date")