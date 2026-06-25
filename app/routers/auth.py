from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models import User
from app.schemas.auth import UserCreate, UserResponse, Token
from security import hash_password, verify_password, create_access_token
from app.dependencies import get_current_user
from app.logger import logger

router = APIRouter(tags=["Authentication"])


@router.post("/register",response_model=UserResponse,status_code=status.HTTP_201_CREATED)
def register_user(user:UserCreate,db:Session=Depends(get_db)):
    logger.info(f"Attempting to register user: username='{user.username}', email='{user.email}'")
    existing_user = (
        db.query(User)
        .filter(User.username == user.username)
        .first()
    )   
    if existing_user:
        logger.warning(f"Registration failed: Username '{user.username}' already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    existing_email= (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )
    if existing_email:
        logger.warning(f"Registration failed: Email '{user.email}' already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"User registered successfully: username='{new_user.username}', id={new_user.id}")
    return new_user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    logger.info(f"Login attempt for username: '{form_data.username}'")
    db_user = (
        db.query(User)
        .filter(User.username == form_data.username)
        .first()
    )

    if not db_user:
        logger.warning(f"Login failed: Username '{form_data.username}' not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    if not verify_password(
        form_data.password,
        db_user.hashed_password
    ):
        logger.warning(f"Login failed: Incorrect password for username '{form_data.username}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    token = create_access_token(
        {"sub": db_user.username}
    )

    logger.info(f"Login successful: User '{db_user.username}' logged in")
    return {
        "access_token": token,
        "token_type": "bearer"
    }



@router.get("/me", response_model=UserResponse)
def me_user(current_user: User = Depends(get_current_user)):
    logger.info(f"User profile fetched: username='{current_user.username}'")
    return current_user

