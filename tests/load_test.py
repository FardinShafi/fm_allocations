from locust import HttpUser, task, between

class VehicleAllocationUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def create_allocation(self):
        self.client.post("/api/v1/allocations/", json={
            "employee_id": 1,
            "vehicle_id": 1,
            "allocation_date": "2024-12-01",
            "purpose": "Test"
        })