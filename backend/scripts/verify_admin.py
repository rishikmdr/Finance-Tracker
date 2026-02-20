import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to sys.path so we can import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.security import verify_password
from app.models.user import User

DATABASE_URL = "sqlite:///./finance_tracker.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def verify_admin():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "admin@example.com").first()
        if not user:
            print("ERROR: Admin user NOT found in database.")
            return
        
        print(f"User found: {user.email}")
        print(f"Active: {user.is_active}")
        print(f"Hash: {user.password_hash}")
        
        # Test password verification
        test_pass = "admin@1234"
        is_valid = verify_password(test_pass, user.password_hash)
        print(f"Password verification for '{test_pass}': {is_valid}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_admin()
