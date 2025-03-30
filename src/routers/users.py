import logging
from typing import Sequence

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from ..database import get_session
from ..models import User
from ..schemas import UserCreate, UserRead


router = APIRouter(prefix="/users", tags=["users"])

logger = logging.getLogger(__name__)


@router.post("/", response_model=UserRead)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_session),
) -> User:
    """Create a new user."""
    try:
        new_user = User(name=user.name, email=user.email)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"User created: {new_user.id}")
    except IntegrityError as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=422, detail=str(e))

    return new_user


@router.get("/", response_model=list[UserRead])
async def get_users(
    db: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
) -> Sequence[User]:
    """Retrieve all users."""
    logger.info(f"Getting users with skip: {skip} and limit: {limit}")

    return db.exec(select(User).offset(skip).limit(limit)).all()


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    db: Session = Depends(get_session),
) -> User:
    """Retrieve a user by ID."""
    logger.info(f"Getting user with ID: {user_id}")
    user = db.exec(select(User).where(User.id == user_id)).first()

    if not user:
        logger.error(f"User with ID {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.put("/{user_id}", response_model=UserRead)
async def update_user_email(
    user_id: int,
    email: str,
    db: Session = Depends(get_session),
) -> User:
    """Update a user's email."""
    logger.info(f"Updating user with ID: {user_id} to have email: {email}")
    user = db.exec(select(User).where(User.id == user_id)).first()

    if not user:
        logger.error(f"User with ID {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")

    # Update email and commit changes to database
    user.email = email
    db.commit()
    db.refresh(user)
    logger.info(f"User with ID {user_id} updated to have email: {email}")

    return user
