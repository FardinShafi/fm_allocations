from pymongo import MongoClient

def test_connection():
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client.vehicle_allocation
        test_collection = db.test
        test_collection.insert_one({"test": "connection"})
        result = test_collection.find_one({"test": "connection"})
        
        if result:
            print("MongoDB is working correctly!")
        
        test_collection.drop()
        
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    test_connection()