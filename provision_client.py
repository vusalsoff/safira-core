import sqlite3
import uuid
import secrets
import hashlib
import sys

def provision(name: str, db_path: str = "safira.db"):
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    
    # Check if api_clients table exists
    try:
        cursor.execute("SELECT 1 FROM api_clients LIMIT 1")
    except sqlite3.OperationalError:
        print("Database not initialized with API clients table.")
        sys.exit(1)
        
    client_id = f"client_{uuid.uuid4().hex[:12]}"
    api_key = f"sk_safira_{secrets.token_urlsafe(32)}"
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    from datetime import datetime
    cursor.execute("INSERT INTO api_clients (id, api_key_hash, name, is_revoked, created_at) VALUES (?, ?, ?, ?, ?)",
                   (client_id, api_key_hash, name, 0, datetime.utcnow().isoformat()))
    db.commit()
    db.close()
    
    print("=" * 50)
    print("SAFIRA CLIENT PROVISIONED SUCCESSFULLY")
    print("=" * 50)
    print(f"Client Name: {name}")
    print(f"Client ID:   {client_id}")
    print(f"API Key:     {api_key}")
    print("=" * 50)
    print("SAVE THIS API KEY NOW. IT WILL NOT BE SHOWN AGAIN.")
    print("Provide it to the Main AI client as: Authorization: Bearer <API_KEY>")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python provision_client.py <Client_Name> [db_path]")
        sys.exit(1)
    
    name = sys.argv[1]
    db_path = sys.argv[2] if len(sys.argv) > 2 else "safira.db"
    provision(name, db_path)
