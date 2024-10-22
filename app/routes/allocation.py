from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from datetime import date
from app.database import get_database
from app.models.schemas import (
    AllocationCreate,
    AllocationUpdate,
    AllocationResponse,
    AllocationListResponse
)
from app.services.allocation import AllocationService

router = APIRouter()

async def get_allocation_service():
    db = await get_database()
    return AllocationService(db)

@router.post("/allocations/", response_model=AllocationResponse)
async def create_allocation(
    allocation: AllocationCreate,
    service: AllocationService = Depends(get_allocation_service)
):
    try:
        # Create allocation and get the resulting Allocation object
        result = await service.create_allocation(allocation)
        
        return {
            "status": "success",
            "message": "Allocation created successfully",
            "data": result  # `result` should be an instance of Allocation
        }
    except ValueError as e:
        # Return a 400 error for ValueErrors
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Optionally handle other exceptions to avoid leaking information
        raise HTTPException(status_code=500, detail="An error occurred while creating allocation.")

@router.get("/allocations/", response_model=AllocationListResponse)
async def list_allocations(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    service: AllocationService = Depends(get_allocation_service)
):
    allocations = await service.get_allocations(skip, limit)
    return {
        "status": "success",
        "message": "Allocations retrieved successfully",
        "data": allocations  # allocations will be a list of Allocation objects
    }

@router.put("/allocations/{allocation_id}", response_model=AllocationResponse)
async def update_allocation(
    allocation_id: str,
    update_data: AllocationUpdate,
    service: AllocationService = Depends(get_allocation_service)
):
    try:
        result = await service.update_allocation(allocation_id, update_data)
        return {
            "status": "success",
            "message": "Allocation updated successfully",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/allocations/{allocation_id}", response_model=AllocationResponse)
async def delete_allocation(
    allocation_id: str,
    service: AllocationService = Depends(get_allocation_service)
):
    try:
        await service.delete_allocation(allocation_id)
        return {
            "status": "success",
            "message": "Allocation deleted successfully",
            "data": None
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/allocations/history", response_model=AllocationListResponse)
async def get_allocation_history(
    employee_id: Optional[int] = Query(None, description="Filter by employee ID"),
    vehicle_id: Optional[int] = Query(None, description="Filter by vehicle ID"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(10, ge=1, description="Maximum number of records to return"),
    sort_by: str = Query("allocation_date", description="Field to sort by"),
    sort_order: int = Query(-1, description="Sort order: 1 for ascending, -1 for descending"),
    service: AllocationService = Depends(get_allocation_service)
):
    # Fetch allocations with pagination and sorting
    allocations = await service.get_allocation_history(
        employee_id, vehicle_id, start_date, end_date, skip, limit, sort_by, sort_order
    )
    
    return {
        "status": "success",
        "message": "Allocation history retrieved successfully",
        "data": allocations
    }