import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Default to a local instance if not provided, but we expect it in .env
# Default to a local instance if not provided, but we expect it in .env
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "voice_assistant_db")

def get_db_connection():
    """
    Establishes a connection to the MongoDB database.
    """
    try:
        # Reduced timeout for faster failure
        print(f"DEBUG: Connecting to MongoDB at {MONGO_URI.split('@')[-1] if '@' in MONGO_URI else 'localhost'}...")
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Check if connection is successful
        client.admin.command('ping')
        return client[DB_NAME]
    except Exception as e:
        print(f"✗ Failed to connect to MongoDB: {e}")
        return None

def seed_db():
    print("⚠️  Skipping seed_db() for remote database to protect data.")

def get_whole_database():
    """
    Dynamically fetches ALL data from ALL collections in the database.
    CAUTION: For large remote databases, this might be slow.
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
            
        # LIMITATION: Fetch only first 3 docs per collection for the schemas
        cursor = db[col_name].find({}, {"_id": 0}).limit(3)
        records = list(cursor)
        whole_db[col_name] = records
        
    return whole_db

def get_database_schema(mode="summary", collection_name=None):
    """
    Returns database structure.
    mode="summary": Returns list of all collection names (Low token usage).
    mode="detail": Returns fields for a specific collection (High token usage).
    """
    db = get_db_connection()
    if db is None:
        return {}
    
    if mode == "detail" and collection_name:
        if collection_name not in db.list_collection_names():
            return {"error": "Collection not found"}
        sample = db[collection_name].find_one()
        if sample:
            keys = [k for k in sample.keys() if k != "_id"]
            return {collection_name: keys}
        return {collection_name: []}

    # Summary Mode (Default)
    cols = db.list_collection_names()
    clean_cols = [c for c in cols if not c.startswith("system.")]
    return {"collections": clean_cols}

def find_documents(collection_name, query={}, limit=10):
    """
    Executes a dynamic find query on a specific collection.
    Handles LLM 'hallucinations' where it puts options inside the query.
    """
    db = get_db_connection()
    if db is None: return []
    
    try:
        if collection_name not in db.list_collection_names():
            return [f"Error: Collection '{collection_name}' does not exist."]
            
        # 1. Clean the query (Extract options if the LLM put them inside)
        clean_query = query.copy()
        sort_option = clean_query.pop("sort", None)
        projection_option = clean_query.pop("projection", {"_id": 0}) # Default to hiding _id
        
        # Override limit if passed inside query
        if "limit" in clean_query:
             limit = clean_query.pop("limit")

        # 2. Safety Limit
        safe_limit = min(int(limit), 50) 
        
        # 3. Construct Cursor
        cursor = db[collection_name].find(clean_query, projection_option)
        
        # 4. Apply Sort
        if sort_option:
            # Handle {"field": -1} or simple "field" string
            if isinstance(sort_option, str):
                cursor = cursor.sort(sort_option, 1) # Default to ascending
            elif isinstance(sort_option, dict):
                for k, v in sort_option.items():
                    cursor = cursor.sort(k, int(v))
        
        cursor = cursor.limit(safe_limit)
        return list(cursor)
    except Exception as e:
        return [f"Database Error: {e}"]

def test_connection():
    print(f"🔌 Connecting to: {DB_NAME}...")
    db = get_db_connection()
    if db is not None:
        print("✓ Connection Successful!")
        cols = db.list_collection_names()
        print(f"📚 Found {len(cols)} collections: {cols}")
    else:
        print("✗ Connection Failed.")

if __name__ == "__main__":
    print("--- Testing Database Connection ---")
    test_connection()
