import pytest
from httpx import AsyncClient
from app.main import app
from datetime import date, timedelta

@pytest.mark.asyncio
async def test_create_allocation():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/allocations/", json={
            "employee_id": 1,
            "vehicle_id": 1,
            "allocation_date": (date.today() + timedelta(days=1)).isoformat(),
            "purpose": "Test Purpose"
        })
        assert response.status_code == 200
        assert response.json()["status"] == "success"