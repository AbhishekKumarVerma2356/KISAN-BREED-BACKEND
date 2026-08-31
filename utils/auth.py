from uuid import UUID

from fastapi import (
    Depends,
    HTTPException,
    status
)

from fastapi.security import (
    OAuth2PasswordBearer
)

from jose import (
    JWTError,
    jwt
)

from sqlalchemy.orm import Session

from utils.database import get_db

from models.user import User


# =========================================================
# JWT CONFIGURATION
# =========================================================

SECRET_KEY = "CHANGE_THIS_TO_YOUR_REAL_SECRET_KEY"

ALGORITHM = "HS256"


# =========================================================
# TOKEN READER
# =========================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/login"
)


# =========================================================
# GET CURRENT USER
# =========================================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate authentication credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if not user_id:

            raise credentials_exception

        user_uuid = UUID(
            str(user_id)
        )

    except (
        JWTError,
        ValueError,
        TypeError
    ):

        raise credentials_exception

    # -------------------------------------------------------
    # FIND USER
    # -------------------------------------------------------

    user = (
        db.query(User)
        .filter(
            User.id == user_uuid
        )
        .first()
    )

    if not user:

        raise credentials_exception

    return user