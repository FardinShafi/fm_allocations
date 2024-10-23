from datetime import date
from pydantic import BaseModel, Field
from typing import Optional, List
from bson import ObjectId

class AllocationBase(BaseModel):
    employee_id: int
    vehicle_id: int
    allocation_date: date  # Keep this as date if you want only the date part
    purpose: str

class AllocationCreate(AllocationBase):
    pass

class AllocationUpdate(BaseModel):
    employee_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    allocation_date: Optional[date] = None
    purpose: Optional[str] = None

class Allocation(AllocationBase):
    id: str = Field(..., alias="_id")  # Maintain the alias for MongoDB's ObjectId

    class Config:
        # Convert ObjectId to str for the response
        json_encoders = {
            ObjectId: str
        }

class AllocationResponse(BaseModel):
    status: str
    message: str
    data: Optional[Allocation] = None

class AllocationListResponse(BaseModel):
    status: str
    message: str
    data: List[Allocation]
