import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserRole(str, enum.Enum):
    OWNER = "owner"
    MEMBER = "member"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Family relationship
    family_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("families.id"), nullable=True
    )
    family_role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.OWNER
    )

    family: Mapped["Family | None"] = relationship("Family", back_populates="members")

    # Holdings relationships
    stock_holdings: Mapped[list["StockHolding"]] = relationship(back_populates="user")
    mf_holdings: Mapped[list["MFHolding"]] = relationship(back_populates="user")
    sips: Mapped[list["SIP"]] = relationship(back_populates="user")
    fixed_holdings: Mapped[list["FixedHolding"]] = relationship(back_populates="user")
    property_holdings: Mapped[list["PropertyHolding"]] = relationship(back_populates="user")
    gold_holdings: Mapped[list["GoldHolding"]] = relationship(back_populates="user")
    liabilities: Mapped[list["Liability"]] = relationship(back_populates="user")
    incomes: Mapped[list["Income"]] = relationship(back_populates="user")
    expenses: Mapped[list["Expense"]] = relationship(back_populates="user")


class Family(Base):
    __tablename__ = "families"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    members: Mapped[list[User]] = relationship("User", back_populates="family")
