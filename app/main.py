from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import allocation
from app.database import get_database, create_indexes

app = FastAPI(title="Vehicle Allocation System")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(allocation.router, prefix="/api/v1", tags=["allocations"])

# Startup event to create indexes
@app.on_event("startup")
async def startup_event():
    db = await get_database()
    await create_indexes(db)