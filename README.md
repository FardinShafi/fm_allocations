# Vehicle Allocation System

A FastAPI-based REST API service for managing vehicle allocations to employees. This system provides endpoints to create, read, update, and delete vehicle allocations while maintaining data integrity through MongoDB indexes.

## Features

- Async MongoDB integration with connection pooling
- FastAPI REST API endpoints
- CORS middleware enabled
- Automated index creation for optimal query performance
- Environment-based configuration
- Pydantic models for request/response validation

## Prerequisites

- Python 3.7+
- MongoDB 4.0+
- pip (Python package manager)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd vehicle-allocation-system
```

2. Create and activate a virtual environment:

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Or just manually create a file and name it .env

2. Configure your environment variables in `.env`:

```
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=vehicle_allocation
```

Adjust the `MONGODB_URL` if your MongoDB instance is hosted elsewhere or requires authentication.

## Running the Application

1. Start MongoDB:

```bash
# If running MongoDB locally
mongod
```

/
[I used MongoDBCompass]

2. Insert seed data:

```bash
python scripts/seed_data.py
```

### This will insert seed data into database, employees, vehicles, drivers will have id from 1-1000 that can be later used for the APIs.

3. Start the FastAPI server:

```bash
# Development server
uvicorn app.main:app --reload
OR
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## Testing

In a seperate terminal, open a virtual environment while the server is running in the first terminal.
Then run these tests.

1. MongoDB connection test:

```bash
python -m tests.test_mongodb
```

2. load testing

```bash
python -m tests.load_test
```

## API Documentation

Once the server is running, you can access:

- Interactive API documentation (Swagger UI): `http://localhost:8000/docs`
- Alternative API documentation (ReDoc): `http://localhost:8000/redoc`

## API Endpoints

The API is versioned and all endpoints are prefixed with `/api/v1`:

### Allocations

- `POST /api/v1/allocations` - Create a new vehicle allocation
- `GET /api/v1/allocations` - List all allocations
- `GET /api/v1/allocations/{id}` - Get a specific allocation
- `PUT /api/v1/allocations/{id}` - Update an allocation
- `DELETE /api/v1/allocations/{id}` - Delete an allocation
- `GET /api/v1/allocations/history` - List all allocations with filters, pagination and search and sorting

## Database Indexes

The system automatically creates the following indexes on startup:

1. Compound index on `vehicle_id` and `allocation_date` (unique)
2. Compound index on `employee_id` and `allocation_date`
3. Compound index on `employee_id`, `vehicle_id`, and `allocation_date`

These indexes optimize query performance for common operations.

## Error Handling

The API uses standard HTTP status codes and returns responses in the following format:

```json
{
    "status": "success|error",
    "message": "Description of the result",
    "data": null | object | array
}
```

## Development

The project uses:

- FastAPI for the web framework
- Motor for async MongoDB operations
- Pydantic for data validation
- python-dotenv for environment management

## Deployement

The project can be deployed on any Linux server (like Ubuntu) that has Python 3.7+ and MongoDB installed. You'd need to copy your code to the server, set up a Python virtual environment, install dependencies from requirements.txt, and configure your .env file with the production database settings. To keep the application running continuously, you can use a process manager like Supervisor or systemd. For maintenance, you'll mainly need to monitor the application logs for errors, periodically backup your MongoDB database, and update your code by pulling the latest changes from your repository and restarting the application. Regular system updates and disk space monitoring are also important for server health.
The whole setup can be done in a short time, and once running, maintenance typically involves just checking logs daily and doing updates when you push new code changes. No special infrastructure or complex setup is needed since this is a relatively straightforward Python/FastAPI application. Docker can also be used to deploy and work on if you are looking for a more standard/structured approach.
