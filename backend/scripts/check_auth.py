import sys
import os
from sqlalchemy import create_engine, text

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.security import verify_password, hash_password

DATABASE_URL = "sqlite:///./finance_tracker.db"
engine = create_engine(DATABASE_URL)

def check_db_content():
    print("--- Database Check ---")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT email, password_hash, is_active FROM users WHERE email = 'admin@example.com'"))
        row = result.fetchone()
        if row:
            print(f"User email: {row[0]}")
            print(f"Is active: {row[2]}")
            print(f"Stored hash: {row[1]}")
            
            # Test verification directly
            password = "admin@1234"
            try:
                is_valid = verify_password(password, row[1])
                print(f"Verification of '{password}': {is_valid}")
            except Exception as e:
                print(f"Verification ERROR: {e}")
        else:
            print("Admin user NOT found.")

    print("\n--- Library Check ---")
    try:
        test_pass = "test1234"
        hashed = hash_password(test_pass)
        print(f"Hashed '{test_pass}': {hashed}")
        is_valid = verify_password(test_pass, hashed)
        print(f"Verification of new hash: {is_valid}")
    except Exception as e:
        print(f"Hashing/Verification ERROR: {e}")

if __name__ == "__main__":
    check_db_content()
