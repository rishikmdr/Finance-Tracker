from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import Family, User, UserRole
from app.schemas.user import (
    FamilyCreate,
    FamilyInvite,
    FamilyResponse,
    TokenRefresh,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=data.email,
        name=data.name,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(data: TokenRefresh, db: Session = Depends(get_db)):
    try:
        payload = decode_token(data.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found")

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


# --- Family ---

@router.post("/family", response_model=FamilyResponse, status_code=status.HTTP_201_CREATED)
def create_family(data: FamilyCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.family_id:
        raise HTTPException(status_code=400, detail="Already part of a family")

    family = Family(name=data.name)
    db.add(family)
    db.flush()

    current_user.family_id = family.id
    current_user.family_role = UserRole.OWNER
    db.commit()
    db.refresh(family)

    return family


@router.post("/family/invite", response_model=UserResponse)
def invite_to_family(
    data: FamilyInvite,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.family_id:
        raise HTTPException(status_code=400, detail="You are not part of a family")
    if current_user.family_role != UserRole.OWNER:
        raise HTTPException(status_code=403, detail="Only family owner can invite members")

    invitee = db.query(User).filter(User.email == data.email).first()
    if not invitee:
        raise HTTPException(status_code=404, detail="User not found. They need to register first.")
    if invitee.family_id:
        raise HTTPException(status_code=400, detail="User is already part of a family")

    invitee.family_id = current_user.family_id
    invitee.family_role = UserRole.MEMBER
    db.commit()
    db.refresh(invitee)

    return invitee


@router.get("/family", response_model=FamilyResponse)
def get_family(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.family_id:
        raise HTTPException(status_code=404, detail="Not part of a family")

    family = db.query(Family).filter(Family.id == current_user.family_id).first()
    return family
