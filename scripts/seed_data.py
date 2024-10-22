import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def seed_database():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.vehicle_allocation
    
    # Clear existing data
    await db.employees.drop()
    await db.vehicles.drop()
    await db.drivers.drop()
    
    # Insert sample data
    await db.employees.insert_many([
        {"_id": i, "name": f"Employee {i}"} 
        for i in range(1, 1001)
    ])
    
    await db.vehicles.insert_many([
        {"_id": i, "name": f"Vehicle {i}", "driver_id": i}
        for i in range(1, 1001)
    ])
    
    await db.drivers.insert_many([
        {"_id": i, "name": f"Driver {i}"} 
        for i in range(1, 1001)
    ])

if __name__ == "__main__":
    asyncio.run(seed_database())