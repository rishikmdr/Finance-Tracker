import enum
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ImportSource(str, enum.Enum):
    MANUAL = "manual"
    AXIO_CSV = "axio_csv"


class Earner(str, enum.Enum):
    SELF = "self"
    SPOUSE = "spouse"


class IncomeSource(str, enum.Enum):
    SALARY = "salary"
    RENTAL = "rental"
    DIVIDEND = "dividend"
    INTEREST = "interest"
    FREELANCE = "freelance"
    OTHER = "other"


class ExpenseCategory(Base):
    __tablename__ = "expense_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("expense_categories.id"))
    icon: Mapped[str | None] = mapped_column(String(50))
    axio_category_name: Mapped[str | None] = mapped_column(String(100))

    parent: Mapped["ExpenseCategory | None"] = relationship(
        "ExpenseCategory", remote_side="ExpenseCategory.id"
    )
    expenses: Mapped[list["Expense"]] = relationship(back_populates="category")


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    category_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("expense_categories.id")
    )
    description: Mapped[str | None] = mapped_column(Text)
    import_source: Mapped[ImportSource] = mapped_column(
        Enum(ImportSource), nullable=False, default=ImportSource.MANUAL
    )
    axio_ref_id: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="expenses")
    category: Mapped[ExpenseCategory | None] = relationship(back_populates="expenses")


class Income(Base):
    __tablename__ = "incomes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    source: Mapped[IncomeSource] = mapped_column(Enum(IncomeSource), nullable=False)
    earner: Mapped[Earner] = mapped_column(Enum(Earner), nullable=False, default=Earner.SELF)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="incomes")
