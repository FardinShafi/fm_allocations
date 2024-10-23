# from locust import HttpUser, task, between

# class VehicleAllocationUser(HttpUser):
#     wait_time = between(1, 3)

#     @task
#     def create_allocation(self):
#         self.client.post("/api/v1/allocations/", json={
#             "employee_id": 1,
#             "vehicle_id": 1,
#             "allocation_date": "2024-12-01",
#             "purpose": "Test"
#         })

# tests/load_test.py
import asyncio
import aiohttp
import time
from datetime import datetime, timedelta
import random
from concurrent.futures import ThreadPoolExecutor
import statistics
import json

class VehicleAllocationLoadTest:
    def __init__(self, base_url: str, num_users: int, test_duration: int):
        self.base_url = base_url
        self.num_users = num_users
        self.test_duration = test_duration
        self.results = []
        self.errors = []
        self.success_count = 0
        self.fail_count = 0
        
    async def make_request(self, session, endpoint: str, method: str = "GET", data: dict = None):
        start_time = time.time()
        try:
            if method == "GET":
                async with session.get(f"{self.base_url}{endpoint}") as response:
                    response_data = await response.json()
                    if response.status == 200:
                        self.success_count += 1
                    else:
                        self.fail_count += 1
                        self.errors.append({
                            "endpoint": endpoint,
                            "method": method,
                            "data": None,
                            "status": response.status,
                            "response_data": response_data
                        })
            elif method == "POST":
                async with session.post(f"{self.base_url}{endpoint}", json=data) as response:
                    response_data = await response.json()
                    if response.status == 200:
                        self.success_count += 1
                    else:
                        self.fail_count += 1
                        self.errors.append({
                            "endpoint": endpoint,
                            "method": method,
                            "data": data,
                            "status": response.status,
                            "response_data": response_data
                        })
            
            end_time = time.time()
            if response.status == 200:
                self.results.append(end_time - start_time)  # Only log successful responses
            return True
        except Exception as e:
            self.fail_count += 1
            self.errors.append({
                "endpoint": endpoint,
                "method": method,
                "data": data,
                "error_message": str(e)
            })
            print(f"Error: {e}")
            return False

    async def simulate_user(self, user_id: int):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            
            while time.time() - start_time < self.test_duration:
                # Random allocation date in the future
                future_date = datetime.now() + timedelta(days=random.randint(1, 30))
                
                # Create allocation
                allocation_data = {
                    "employee_id": random.randint(1, 100),
                    "vehicle_id": random.randint(1, 50),
                    "allocation_date": future_date.strftime("%Y-%m-%d"),
                    "purpose": f"Test purpose {random.randint(1, 1000)}"
                }
                
                await self.make_request(
                    session,
                    "/api/v1/allocations/",
                    method="POST",
                    data=allocation_data
                )
                
                # Get allocations list
                await self.make_request(
                    session,
                    "/api/v1/allocations/"
                )
                
                # Get allocation history with random filters
                params = {
                    "employee_id": random.randint(1, 100),
                    "vehicle_id": random.randint(1, 50),
                    "skip": random.randint(0, 50),
                    "limit": 10
                }
                query_string = "&".join(f"{k}={v}" for k, v in params.items())
                await self.make_request(
                    session,
                    f"/api/v1/allocations/history?{query_string}"
                )
                
                # Small delay between requests
                await asyncio.sleep(random.uniform(0.1, 0.5))

    async def run(self):
        tasks = [self.simulate_user(i) for i in range(self.num_users)]
        await asyncio.gather(*tasks)
        
        # Calculate statistics
        if self.results:
            avg_response_time = statistics.mean(self.results)
            p95_response_time = statistics.quantiles(self.results, n=20)[18]  # 95th percentile
            p99_response_time = statistics.quantiles(self.results, n=100)[98]  # 99th percentile
            success_rate = (self.success_count / (self.success_count + self.fail_count)) * 100
            
            # Log results to a JSON file
            test_summary = {
                "Total Requests": len(self.results) + len(self.errors),
                "Successful Requests": self.success_count,
                "Failed Requests": self.fail_count,
                "Success Rate": f"{success_rate:.2f}%",
                "Average Response Time": f"{avg_response_time:.3f} seconds",
                "95th Percentile Response Time": f"{p95_response_time:.3f} seconds",
                "99th Percentile Response Time": f"{p99_response_time:.3f} seconds",
                "Requests per Second": f"{(len(self.results) + len(self.errors)) / self.test_duration:.2f}",
                "Errors": self.errors
            }
            
            with open("load_test_results.json", "w") as f:
                json.dump(test_summary, f, indent=4)
                
            print(f"\nLoad Test Results:")
            print(f"Total Requests: {len(self.results) + len(self.errors)}")
            print(f"Successful Requests: {self.success_count}")
            print(f"Failed Requests: {self.fail_count}")
            print(f"Success Rate: {success_rate:.2f}%")
            print(f"Average Response Time: {avg_response_time:.3f} seconds")
            print(f"95th Percentile Response Time: {p95_response_time:.3f} seconds")
            print(f"99th Percentile Response Time: {p99_response_time:.3f} seconds")
            print(f"Requests per Second: {(len(self.results) + len(self.errors)) / self.test_duration:.2f}")

if __name__ == "__main__":
    base_url = "http://localhost:8000"  # Change this to your API URL
    num_concurrent_users = 50
    test_duration_seconds = 60
    
    load_test = VehicleAllocationLoadTest(
        base_url=base_url,
        num_users=num_concurrent_users,
        test_duration=test_duration_seconds
    )
    
    print(f"Starting load test with {num_concurrent_users} concurrent users for {test_duration_seconds} seconds...")
    asyncio.run(load_test.run())
