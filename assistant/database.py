import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Default to a local instance if not provided, but we expect it in .env
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "voice_assistant_db"

def get_db_connection():
    """
    Establishes a connection to the MongoDB database.
    """
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Check if connection is successful
        client.admin.command('ping')
        # print("✓ Connected to MongoDB") # Reduce log noise
        return client[DB_NAME]
    except Exception as e:
        print(f"✗ Failed to connect to MongoDB: {e}")
        return None

def seed_db():
    """
    Populates the database with initial dummy data for multiple collections.
    """
    db = get_db_connection()
    if db is None:
        return

    # 1. Employees
    if db["employees"].count_documents({}) == 0:
        initial_employees = [
            {"id": "1223", "name": "John Doe", "role": "Senior Engineer", "department": "AI Research"},
            {"id": "1224", "name": "Jane Smith", "role": "Product Manager", "department": "Design"},
            {"id": "1225", "name": "Bob Wilson", "role": "Intern", "department": "Coffee Operations"},
            {"id": "1226", "name": "Alice Johnson", "role": "Data Scientist", "department": "Analytics"}
        ]
        db["employees"].insert_many(initial_employees)
        print(f"✓ Seeded 'employees' with {len(initial_employees)} records.")
    
    # 2. Inventory (New!)
    if db["inventory"].count_documents({}) == 0:
        initial_inventory = [
            {"item_id": "A101", "product": "iPhone 15 Pro", "stock": 50, "location": "Warehouse A"},
            {"item_id": "A102", "product": "MacBook Air M3", "stock": 25, "location": "Warehouse B"},
            {"item_id": "B201", "product": "Curved Monitor 34\"", "stock": 10, "location": "Showroom"}
        ]
        db["inventory"].insert_many(initial_inventory)
        print(f"✓ Seeded 'inventory' with {len(initial_inventory)} records.")

def get_whole_database():
    """
    Dynamically fetches ALL data from ALL collections in the database.
    Returns a dictionary: { "collection_name": [list_of_records] }
    """
    db = get_db_connection()
    if db is None:
        return {}

    whole_db = {}
    
    # Get all collection names
    collection_names = db.list_collection_names()
    
    for col_name in collection_names:
        # Skip system collections if any
        if col_name.startswith("system."):
            continue
            
        cursor = db[col_name].find({}, {"_id": 0})
        records = list(cursor)
        whole_db[col_name] = records
        
    return whole_db

if __name__ == "__main__":
    print("--- Testing Dynamic Database Module ---")
    seed_db()
    data = get_whole_database()
    print("Fetched Database Content:")
    import json
    print(json.dumps(data, indent=2))
