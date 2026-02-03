import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Default to a local instance if not provided, but we expect it in .env
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "voice_assistant_db"
COLLECTION_NAME = "employees"

def get_db_connection():
    """
    Establishes a connection to the MongoDB database.
    """
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Check if connection is successful
        client.admin.command('ping')
        print("✓ Connected to MongoDB")
        return client[DB_NAME]
    except Exception as e:
        print(f"✗ Failed to connect to MongoDB: {e}")
        return None

def seed_db():
    """
    Populates the database with initial dummy data.
    Useful for first-time setup.
    """
    db = get_db_connection()
    if db is None:
        return

    employees_collection = db[COLLECTION_NAME]
    
    # Check if data already exists to avoid duplicates
    if employees_collection.count_documents({}) > 0:
        print("Database already has data. Skipping seed.")
        return

    initial_employees = [
        {"id": "1223", "name": "John Doe", "role": "Senior Engineer", "department": "AI Research"},
        {"id": "1224", "name": "Jane Smith", "role": "Product Manager", "department": "Design"},
        {"id": "1225", "name": "Bob Wilson", "role": "Intern", "department": "Coffee Operations"},
        {"id": "1226", "name": "Alice Johnson", "role": "Data Scientist", "department": "Analytics"}
    ]

    employees_collection.insert_many(initial_employees)
    print(f"✓ Seeded database with {len(initial_employees)} employees.")

def get_all_employees():
    """
    Fetches all employee records from the database.
    Returns a list of dictionaries (excluding the MongoDB _id field).
    """
    db = get_db_connection()
    if db is None:
        return []

    employees_collection = db[COLLECTION_NAME]
    
    # helper to exclude internal _id from results
    cursor = employees_collection.find({}, {"_id": 0})
    
    employees = list(cursor)
    return employees

def add_employee(employee_data):
    """
    Adds a new employee to the database.
    """
    db = get_db_connection()
    if db is None:
        return False

    employees_collection = db[COLLECTION_NAME]
    result = employees_collection.insert_one(employee_data)
    print(f"✓ Added employee: {employee_data.get('name')} (ID: {employee_data.get('id')})")
    return True

if __name__ == "__main__":
    # Test strictly when running this file directly
    print("--- Testing Database Module ---")
    seed_db()
    data = get_all_employees()
    print(f"Fetched {len(data)} employees:")
    for emp in data:
        print(emp)
