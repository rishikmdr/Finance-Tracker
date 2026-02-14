import csv
import io
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.expense import Expense, ExpenseCategory, ImportSource, Income
from app.models.user import User
from app.schemas.expense import (
    AxioCSVUploadResponse,
    ExpenseCategoryResponse,
    ExpenseCreate,
    ExpenseResponse,
    IncomeCreate,
    IncomeResponse,
)

router = APIRouter(tags=["expenses & income"])


# ==================== EXPENSE CATEGORIES ====================

@router.get("/expense-categories", response_model=list[ExpenseCategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return db.query(ExpenseCategory).all()


# ==================== EXPENSES ====================

@router.get("/expenses", response_model=list[ExpenseResponse])
def list_expenses(
    month: int | None = None,
    year: int | None = None,
    category_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Expense).filter(Expense.user_id == user.id)
    if month and year:
        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1)
        else:
            end = date(year, month + 1, 1)
        query = query.filter(Expense.date >= start, Expense.date < end)
    if category_id:
        query = query.filter(Expense.category_id == category_id)
    return query.order_by(Expense.date.desc()).all()


@router.post("/expenses", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    data: ExpenseCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    expense = Expense(user_id=user.id, import_source=ImportSource.MANUAL, **data.model_dump())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    expense = (
        db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == user.id).first()
    )
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(expense)
    db.commit()


# ==================== AXIO CSV IMPORT ====================

@router.post("/expenses/import/axio", response_model=AxioCSVUploadResponse)
async def import_axio_csv(
    file: UploadFile,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file")

    content = await file.read()
    text = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))

    rows = list(reader)
    if not rows:
        raise HTTPException(status_code=400, detail="CSV file is empty")

    new_rows = 0
    duplicate_rows = 0
    preview = []

    for row in rows:
        # Axio CSV expected columns: Date, Description, Amount, Category
        # Adapt field names as needed when real Axio CSVs are tested
        row_date_str = row.get("Date", row.get("date", ""))
        row_amount_str = row.get("Amount", row.get("amount", "0"))
        row_desc = row.get("Description", row.get("description", ""))
        row_category = row.get("Category", row.get("category", ""))

        try:
            # Try common date formats
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y"):
                try:
                    row_date = date.fromisoformat(row_date_str) if fmt == "%Y-%m-%d" else None
                    if row_date is None:
                        from datetime import datetime as dt
                        row_date = dt.strptime(row_date_str, fmt).date()
                    break
                except (ValueError, TypeError):
                    continue
            else:
                continue  # Skip rows with unparseable dates

            amount = abs(float(row_amount_str.replace(",", "")))
        except (ValueError, TypeError):
            continue

        # Deduplication check
        existing = (
            db.query(Expense)
            .filter(
                Expense.user_id == user.id,
                Expense.date == row_date,
                Expense.amount == amount,
                Expense.description == row_desc,
                Expense.import_source == ImportSource.AXIO_CSV,
            )
            .first()
        )

        if existing:
            duplicate_rows += 1
            continue

        # Find matching category
        category = None
        if row_category:
            category = (
                db.query(ExpenseCategory)
                .filter(ExpenseCategory.axio_category_name == row_category)
                .first()
            )

        expense = Expense(
            user_id=user.id,
            date=row_date,
            amount=amount,
            category_id=category.id if category else None,
            description=row_desc,
            import_source=ImportSource.AXIO_CSV,
        )
        db.add(expense)
        new_rows += 1

        if len(preview) < 10:
            preview.append({
                "date": str(row_date),
                "amount": amount,
                "description": row_desc,
                "category": row_category,
                "status": "imported",
            })

    db.commit()

    return AxioCSVUploadResponse(
        total_rows=len(rows),
        new_rows=new_rows,
        duplicate_rows=duplicate_rows,
        preview=preview,
    )


# ==================== INCOME ====================

@router.get("/income", response_model=list[IncomeResponse])
def list_income(
    month: int | None = None,
    year: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Income).filter(Income.user_id == user.id)
    if month and year:
        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1)
        else:
            end = date(year, month + 1, 1)
        query = query.filter(Income.date >= start, Income.date < end)
    return query.order_by(Income.date.desc()).all()


@router.post("/income", response_model=IncomeResponse, status_code=status.HTTP_201_CREATED)
def create_income(
    data: IncomeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    income = Income(user_id=user.id, **data.model_dump())
    db.add(income)
    db.commit()
    db.refresh(income)
    return income


@router.delete("/income/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_income(
    income_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    income = db.query(Income).filter(Income.id == income_id, Income.user_id == user.id).first()
    if not income:
        raise HTTPException(status_code=404, detail="Income entry not found")
    db.delete(income)
    db.commit()
