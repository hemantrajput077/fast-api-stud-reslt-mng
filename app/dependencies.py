from fastapi import ( Depends, HTTPException, status)
from fastapi.security import OAuth2PasswordBearer
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from database import get_db
from models import User
from security import decode_access_token


oauth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")




async def get_current_user(
    token: str = Depends(oauth_scheme),
    db: Session = Depends(get_db)
):
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    username = payload.get("sub")

    user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user
    
