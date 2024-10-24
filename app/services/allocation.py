from datetime import date, datetime
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.models.schemas import AllocationCreate, AllocationUpdate,  Allocation

class AllocationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def create_allocation(self, allocation: AllocationCreate) -> dict:
        # Convert the allocation_date to a datetime object
        allocation_date = datetime.combine(allocation.allocation_date, datetime.min.time())
        
        # Check if the vehicle is already allocated for the date
        existing_vehicle_allocation = await self.db.allocations.find_one({
            "vehicle_id": allocation.vehicle_id,
            "allocation_date": allocation_date  # Use the datetime object here
        })
        if existing_vehicle_allocation:
            raise ValueError("Vehicle already allocated for this date")

        # Check if the employee is already allocated a vehicle for the same date
        existing_employee_allocation = await self.db.allocations.find_one({
            "employee_id": allocation.employee_id,
            "allocation_date": allocation_date  # Check if the employee is already allocated for the same date
        })
        if existing_employee_allocation:
            raise ValueError("This employee already has allocated a vehicle for themselves at this date")

        # Check if the allocation date is in the future
        if allocation.allocation_date <= date.today():
            raise ValueError("Allocation date must be in the future")

        # Create allocation (store the datetime object)
        allocation_dict = allocation.model_dump()
        allocation_dict["allocation_date"] = allocation_date  # Update the dict with the datetime

        result = await self.db.allocations.insert_one(allocation_dict)
        
        # Convert ObjectId to string
        allocation_data = await self.db.allocations.find_one({"_id": result.inserted_id})
        allocation_data["_id"] = str(allocation_data["_id"])  # Convert ObjectId to string

        return allocation_data
    
    async def get_allocation(self, allocation_id: str) -> Allocation:
        # Convert the allocation_id string to ObjectId
        allocation_object_id = ObjectId(allocation_id)
        
        # Fetch the allocation from the database
        allocation = await self.db.allocations.find_one({"_id": allocation_object_id})
        
        if allocation:
            # Convert ObjectId to string for the _id field
            allocation["_id"] = str(allocation["_id"])
            return Allocation(**allocation)  # Return Allocation instance
        return None  # Return None if not found


    async def get_allocations(self, skip: int = 0, limit: int = 10) -> List[Allocation]:
        cursor = self.db.allocations.find().skip(skip).limit(limit)
        allocations = await cursor.to_list(length=limit)

        # Convert ObjectId to string for the _id field
        for allocation in allocations:
            allocation["_id"] = str(allocation["_id"])  # Convert ObjectId to string

        # Now create Allocation instances
        return [Allocation(**allocation) for allocation in allocations]

    async def update_allocation(self, allocation_id: str, update_data: AllocationUpdate) -> dict:
        # Fetch the current allocation
        allocation = await self.get_allocation(allocation_id)
        if not allocation:
            raise ValueError("Allocation not found")

        # Check if allocation date has passed (existing allocation date)
        if allocation.allocation_date <= date.today():
            raise ValueError("Cannot update past allocations")

        # Prepare the update dictionary
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}

        # If updating allocation_date, vehicle_id, or employee_id, ensure constraints are met
        if update_data.allocation_date or update_data.vehicle_id or update_data.employee_id:
            # Convert allocation_date to datetime if present in update
            new_allocation_date = allocation.allocation_date
            if update_data.allocation_date:
                new_allocation_date = datetime.combine(update_data.allocation_date, datetime.min.time())

            # Check if the allocation date is in the future
            if new_allocation_date.date() <= date.today():
                raise ValueError("Allocation date must be in the future")

            # If vehicle_id is being updated, check if it's different from the existing one
            if update_data.vehicle_id and update_data.vehicle_id != allocation.vehicle_id:
                existing_vehicle_allocation = await self.db.allocations.find_one({
                    "vehicle_id": update_data.vehicle_id,
                    "allocation_date": new_allocation_date
                })
                if existing_vehicle_allocation and existing_vehicle_allocation["_id"] != allocation_id:
                    raise ValueError("Vehicle already allocated for this date")

            # If employee_id is being updated, check if it's different from the existing one
            if update_data.employee_id and update_data.employee_id != allocation.employee_id:
                existing_employee_allocation = await self.db.allocations.find_one({
                    "employee_id": update_data.employee_id,
                    "allocation_date": new_allocation_date
                })
                if existing_employee_allocation and existing_employee_allocation["_id"] != allocation_id:
                    raise ValueError("This employee already has an allocated vehicle for this date")

            # If allocation_date is being updated, add it to update_dict
            if update_data.allocation_date:
                update_dict["allocation_date"] = new_allocation_date

        # If there are updates to apply, perform the update in the database
        if update_dict:
            await self.db.allocations.update_one(
                {"_id": ObjectId(allocation_id)},
                {"$set": update_dict}
            )

        # Return the updated allocation
        return await self.get_allocation(allocation_id)

        

    async def delete_allocation(self, allocation_id: str):
        allocation = await self.get_allocation(allocation_id)
        if not allocation:
            raise ValueError("Allocation not found")

        # Check if allocation date has passed
        if allocation.allocation_date <= date.today():  # Use dot notation
            raise ValueError("Cannot delete past allocations")

        await self.db.allocations.delete_one({"_id": ObjectId(allocation_id)})

    async def get_allocation_history(
            self, 
            employee_id: Optional[int] = None,
            vehicle_id: Optional[int] = None,
            start_date: Optional[date] = None,
            end_date: Optional[date] = None,
            skip: int = 0,  # Pagination: skip the first N results
            limit: int = 10,  # Pagination: limit the number of results
            sort_by: str = "allocation_date",  # Sorting: field to sort by
            sort_order: int = -1  # Sorting: 1 for ascending, -1 for descending
        ) -> list:
        query = {}
        
        # Filter by employee_id
        if employee_id:
            query["employee_id"] = employee_id
        
        # Filter by vehicle_id
        if vehicle_id:
            query["vehicle_id"] = vehicle_id
        
        # Filter by allocation_date range (start_date to end_date)
        if start_date or end_date:
            query["allocation_date"] = {}
            if start_date:
                query["allocation_date"]["$gte"] = datetime.combine(start_date, datetime.min.time())
            if end_date:
                query["allocation_date"]["$lte"] = datetime.combine(end_date, datetime.min.time())

        # Apply pagination and sorting
        cursor = self.db.allocations.find(query).skip(skip).limit(limit).sort(sort_by, sort_order)
        
        # Fetch the allocation documents
        allocations = await cursor.to_list(length=limit)

        # Convert ObjectId to string for serialization
        for allocation in allocations:
            allocation["_id"] = str(allocation["_id"])  # Convert ObjectId to string

        return allocations


