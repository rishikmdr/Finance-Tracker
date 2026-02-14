from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.holdings import (
    FixedHolding,
    GoldHolding,
    Liability,
    MFHolding,
    PropertyHolding,
    SIP,
    StockHolding,
)
from app.models.user import User
from app.schemas.holdings import (
    FixedHoldingCreate,
    FixedHoldingResponse,
    GoldHoldingCreate,
    GoldHoldingResponse,
    LiabilityCreate,
    LiabilityResponse,
    MFHoldingCreate,
    MFHoldingResponse,
    PropertyHoldingCreate,
    PropertyHoldingResponse,
    SIPCreate,
    SIPResponse,
    StockHoldingCreate,
    StockHoldingResponse,
    StockHoldingUpdate,
)

router = APIRouter(prefix="/holdings", tags=["holdings"])


# ==================== STOCKS ====================

@router.get("/stocks", response_model=list[StockHoldingResponse])
def list_stocks(
    investment_type: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(StockHolding).filter(StockHolding.user_id == user.id)
    if investment_type:
        query = query.filter(StockHolding.investment_type == investment_type)
    return query.all()


@router.post("/stocks", response_model=StockHoldingResponse, status_code=status.HTTP_201_CREATED)
def create_stock(
    data: StockHoldingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    holding = StockHolding(user_id=user.id, **data.model_dump())
    db.add(holding)
    db.commit()
    db.refresh(holding)
    return holding


@router.put("/stocks/{holding_id}", response_model=StockHoldingResponse)
def update_stock(
    holding_id: int,
    data: StockHoldingUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    holding = (
        db.query(StockHolding)
        .filter(StockHolding.id == holding_id, StockHolding.user_id == user.id)
        .first()
    )
    if not holding:
        raise HTTPException(status_code=404, detail="Stock holding not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(holding, field, value)
    db.commit()
    db.refresh(holding)
    return holding


@router.delete("/stocks/{holding_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stock(
    holding_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    holding = (
        db.query(StockHolding)
        .filter(StockHolding.id == holding_id, StockHolding.user_id == user.id)
        .first()
    )
    if not holding:
        raise HTTPException(status_code=404, detail="Stock holding not found")
    db.delete(holding)
    db.commit()


# ==================== MUTUAL FUNDS ====================

@router.get("/mf", response_model=list[MFHoldingResponse])
def list_mf(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(MFHolding).filter(MFHolding.user_id == user.id).all()


@router.post("/mf", response_model=MFHoldingResponse, status_code=status.HTTP_201_CREATED)
def create_mf(
    data: MFHoldingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    holding = MFHolding(user_id=user.id, **data.model_dump())
    db.add(holding)
    db.commit()
    db.refresh(holding)
    return holding


@router.delete("/mf/{holding_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mf(
    holding_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    holding = (
        db.query(MFHolding).filter(MFHolding.id == holding_id, MFHolding.user_id == user.id).first()
    )
    if not holding:
        raise HTTPException(status_code=404, detail="MF holding not found")
    db.delete(holding)
    db.commit()


# ==================== SIPs ====================

@router.get("/sips", response_model=list[SIPResponse])
def list_sips(
    active_only: bool = True,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(SIP).filter(SIP.user_id == user.id)
    if active_only:
        query = query.filter(SIP.is_active == True)  # noqa: E712
    return query.all()


@router.post("/sips", response_model=SIPResponse, status_code=status.HTTP_201_CREATED)
def create_sip(
    data: SIPCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    sip = SIP(user_id=user.id, **data.model_dump())
    db.add(sip)
    db.commit()
    db.refresh(sip)
    return sip


@router.put("/sips/{sip_id}/pause", response_model=SIPResponse)
def pause_sip(
    sip_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    sip = db.query(SIP).filter(SIP.id == sip_id, SIP.user_id == user.id).first()
    if not sip:
        raise HTTPException(status_code=404, detail="SIP not found")
    sip.is_active = not sip.is_active
    db.commit()
    db.refresh(sip)
    return sip


@router.delete("/sips/{sip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sip(
    sip_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    sip = db.query(SIP).filter(SIP.id == sip_id, SIP.user_id == user.id).first()
    if not sip:
        raise HTTPException(status_code=404, detail="SIP not found")
    db.delete(sip)
    db.commit()


# ==================== FIXED INCOME ====================

@router.get("/fixed", response_model=list[FixedHoldingResponse])
def list_fixed(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(FixedHolding).filter(FixedHolding.user_id == user.id).all()


@router.post("/fixed", response_model=FixedHoldingResponse, status_code=status.HTTP_201_CREATED)
def create_fixed(
    data: FixedHoldingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    holding = FixedHolding(user_id=user.id, **data.model_dump())
    db.add(holding)
    db.commit()
    db.refresh(holding)
    return holding


@router.delete("/fixed/{holding_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fixed(
    holding_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    holding = (
        db.query(FixedHolding)
        .filter(FixedHolding.id == holding_id, FixedHolding.user_id == user.id)
        .first()
    )
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")
    db.delete(holding)
    db.commit()


# ==================== PROPERTY ====================

@router.get("/property", response_model=list[PropertyHoldingResponse])
def list_property(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(PropertyHolding).filter(PropertyHolding.user_id == user.id).all()


@router.post(
    "/property", response_model=PropertyHoldingResponse, status_code=status.HTTP_201_CREATED
)
def create_property(
    data: PropertyHoldingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    holding = PropertyHolding(user_id=user.id, **data.model_dump())
    db.add(holding)
    db.commit()
    db.refresh(holding)
    return holding


@router.delete("/property/{holding_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property(
    holding_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    holding = (
        db.query(PropertyHolding)
        .filter(PropertyHolding.id == holding_id, PropertyHolding.user_id == user.id)
        .first()
    )
    if not holding:
        raise HTTPException(status_code=404, detail="Property not found")
    db.delete(holding)
    db.commit()


# ==================== GOLD ====================

@router.get("/gold", response_model=list[GoldHoldingResponse])
def list_gold(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(GoldHolding).filter(GoldHolding.user_id == user.id).all()


@router.post("/gold", response_model=GoldHoldingResponse, status_code=status.HTTP_201_CREATED)
def create_gold(
    data: GoldHoldingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    holding = GoldHolding(user_id=user.id, **data.model_dump())
    db.add(holding)
    db.commit()
    db.refresh(holding)
    return holding


@router.delete("/gold/{holding_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_gold(
    holding_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    holding = (
        db.query(GoldHolding)
        .filter(GoldHolding.id == holding_id, GoldHolding.user_id == user.id)
        .first()
    )
    if not holding:
        raise HTTPException(status_code=404, detail="Gold holding not found")
    db.delete(holding)
    db.commit()


# ==================== LIABILITIES ====================

@router.get("/liabilities", response_model=list[LiabilityResponse])
def list_liabilities(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Liability).filter(Liability.user_id == user.id).all()


@router.post(
    "/liabilities", response_model=LiabilityResponse, status_code=status.HTTP_201_CREATED
)
def create_liability(
    data: LiabilityCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    liability = Liability(user_id=user.id, **data.model_dump())
    db.add(liability)
    db.commit()
    db.refresh(liability)
    return liability


@router.delete("/liabilities/{liability_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_liability(
    liability_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    liability = (
        db.query(Liability)
        .filter(Liability.id == liability_id, Liability.user_id == user.id)
        .first()
    )
    if not liability:
        raise HTTPException(status_code=404, detail="Liability not found")
    db.delete(liability)
    db.commit()
