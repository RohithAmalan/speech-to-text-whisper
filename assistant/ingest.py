
import os
import json
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

# Fix relative import for standalone execution
if __name__ == "__main__":
    import sys
    sys.path.append(os.getcwd())
    from assistant import database
else:
    from . import database

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge_store")
os.makedirs(KNOWLEDGE_DIR, exist_ok=True)

VECTORIZER_PATH = os.path.join(KNOWLEDGE_DIR, "tfidf_vectorizer.pkl")
MATRIX_PATH = os.path.join(KNOWLEDGE_DIR, "tfidf_matrix.pkl")
DOCS_PATH = os.path.join(KNOWLEDGE_DIR, "documents.json")

def ingest_data():
    print("🚀 Starting TF-IDF Ingestion (Lock-Free)...")
    print(f"📁 Storage Path: {KNOWLEDGE_DIR}")
    
    # 1. Fetch Data
    print("📥 Fetching data from MongoDB...")
    whole_db = database.get_whole_database()
    
    documents = []
    
    # 2. Process Data
    count = 0
    for col_name, records in whole_db.items():
        if not records: continue
        
        print(f"   Processing {col_name} ({len(records)} records)...")
        
        for doc in records:
            # Flatten doc to string
            text_representation = f"Collection: {col_name}\n"
            text_representation += json.dumps(doc, default=str, indent=0).replace("{", "").replace("}", "").replace('"', "")
            
            documents.append({
                "id": f"{col_name}_{count}",
                "text": text_representation,
                "source": col_name
            })
            count += 1

    # 3. Vectorize & Save
    if documents:
        print(f"⚡ Vectorizing {len(documents)} documents...")
        texts = [d["text"] for d in documents]
        
        # TF-IDF Vectorization
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(texts)
        
        # Save to disk
        print("💾 Saving to disk...")
        with open(VECTORIZER_PATH, "wb") as f:
            pickle.dump(vectorizer, f)
            
        with open(MATRIX_PATH, "wb") as f:
            pickle.dump(tfidf_matrix, f)
            
        with open(DOCS_PATH, "w") as f:
            json.dump(documents, f, indent=2)
            
        print(f"✅ Ingestion Complete! Saved {len(documents)} records.")
    else:
        print("⚠️  No data found to ingest.")

if __name__ == "__main__":
    ingest_data()
