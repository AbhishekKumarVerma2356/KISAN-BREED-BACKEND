from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from utils.database import get_db
from models.user import User
from schemas.auth_schema import UserLogin

from utils.security import verify_password
from utils.jwt_handler import create_access_token

router = APIRouter(
    prefix="/admin",
    tags=["Admin Authentication"]
)

@router.post("/login")
def admin_login(
    user: UserLogin,
    db: Session = Depends(get_db)
):

    db_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        user.password,
        db_user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if db_user.role.lower() != "admin":
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to access Admin Panel."
        )

    token = create_access_token(
        {
            "sub": str(db_user.id),
            "role": "admin"
        }
    )

    return {
        "message": "Admin Login Successful",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(db_user.id),
            "full_name": db_user.full_name,
            "email": db_user.email,
            "role": db_user.role
        }
    }