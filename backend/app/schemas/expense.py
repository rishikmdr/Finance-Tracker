from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.expense import Earner, ImportSource, IncomeSource


class ExpenseCategoryResponse(BaseModel):
    id: int
    name: str
    parent_id: int | None
    icon: str | None

    model_config = {"from_attributes": True}


class ExpenseCreate(BaseModel):
    date: date
    amount: Decimal
    category_id: int | None = None
    description: str | None = None


class ExpenseResponse(BaseModel):
    id: int
    date: date
    amount: Decimal
    category_id: int | None
    category_name: str | None = None
    description: str | None
    import_source: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AxioCSVUploadResponse(BaseModel):
    total_rows: int
    new_rows: int
    duplicate_rows: int
    preview: list[dict]


class IncomeCreate(BaseModel):
    date: date
    amount: Decimal
    source: IncomeSource
    earner: Earner = Earner.SELF
    notes: str | None = None


class IncomeResponse(BaseModel):
    id: int
    date: date
    amount: Decimal
    source: str
    earner: str
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
