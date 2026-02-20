import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to sys.path so we can import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import Base
from app.core.security import hash_password
from app.models.user import User, Family, UserRole
from app.models.holdings import StockHolding, MFHolding, SIP, SIPInstallment, FixedHolding, PropertyHolding, GoldHolding, Liability
from app.models.expense import ExpenseCategory, Expense, Income
from app.models.ai_memory import UserMemory, ChatConversation, ChatMessage, PriceCache
from app.models.extended import FinancialGoal, InsurancePolicy, ESOPHolding, CryptoHolding, TaxDeduction, Notification

DATABASE_URL = "sqlite:///./finance_tracker.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if user already exists
        user = db.query(User).filter(User.email == "admin@example.com").first()
        if not user:
            print("Creating admin user...")
            hashed_pwd = hash_password("admin@1234")
            admin_user = User(
                email="admin@example.com",
                name="Admin User",
                password_hash=hashed_pwd,
                is_active=True,
                family_role=UserRole.OWNER
            )
            db.add(admin_user)
            db.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
