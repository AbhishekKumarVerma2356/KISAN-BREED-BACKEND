from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
)

from jose import JWTError, jwt

from sqlalchemy.orm import Session

from utils.database import get_db

from models.user import User
from models.address import Address
from models.revoked_token import RevokedToken

from schemas.auth_schema import (
    UserSignup,
    UserLogin,
    UpdateProfile,
    ChangePassword,
)

from utils.security import (
    hash_password,
    verify_password,
)

from utils.jwt_handler import (
    create_access_token,
    get_current_user_id,
    SECRET_KEY,
    ALGORITHM,
)


router = APIRouter(
    tags=["Authentication"]
)


security = HTTPBearer()


# =========================================================
# SIGNUP
# =========================================================

@router.post("/signup")
def signup(
    user: UserSignup,
    db: Session = Depends(get_db),
):

    # =====================================================
    # CHECK EXISTING USER
    # =====================================================

    existing_user = (
        db.query(User)
        .filter(
            User.email == user.email
        )
        .first()
    )

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already exists",
        )

    # =====================================================
    # CREATE USER
    # =====================================================

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        contact_number=user.contact_number,
        alternate_contact_number=user.alternate_contact_number,
        password_hash=hash_password(user.password),
        role="customer",
    )

    db.add(new_user)

    # Generate UUID
    db.flush()

    # =====================================================
    # CREATE ADDRESS
    # =====================================================

    new_address = Address(
        user_id=new_user.id,

        address_type=user.address.address_type,

        flat_house_no=user.address.flat_house_no,

        address1=user.address.address1,

        address2=user.address.address2,

        state=user.address.state,

        city_village=user.address.city_village,

        pincode=user.address.pincode,
    )

    db.add(new_address)

    # =====================================================
    # COMMIT
    # =====================================================

    db.commit()

    db.refresh(new_user)
    db.refresh(new_address)

    return {

        "message": "User registered successfully",

        "user": {

            "id": str(new_user.id),

            "full_name": new_user.full_name,

            "email": new_user.email,

            "contact_number": new_user.contact_number,

            "alternate_contact_number":
                new_user.alternate_contact_number,

            "role": new_user.role,
        },

        "address": {

            "id": new_address.id,

            "address_type":
                new_address.address_type,

            "flat_house_no":
                new_address.flat_house_no,

            "address1":
                new_address.address1,

            "address2":
                new_address.address2,

            "state":
                new_address.state,

            "city_village":
                new_address.city_village,

            "pincode":
                new_address.pincode,
        },
    }


# =========================================================
# LOGIN
# =========================================================

@router.post("/login")
def customer_login(
    user: UserLogin,
    db: Session = Depends(get_db),
):

    # =====================================================
    # FIND USER
    # =====================================================

    db_user = (
        db.query(User)
        .filter(
            User.email == user.email
        )
        .first()
    )

    if not db_user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    # =====================================================
    # VERIFY PASSWORD
    # =====================================================

    if not verify_password(
        user.password,
        db_user.password_hash,
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    # =====================================================
    # ADMIN CHECK
    # =====================================================

    if db_user.role.lower() == "admin":

        raise HTTPException(
            status_code=403,
            detail="Admin cannot login from customer portal.",
        )

    # =====================================================
    # CREATE TOKEN
    # =====================================================

    token = create_access_token({
        "sub": str(db_user.id),
    })

    # =====================================================
    # RESPONSE
    # =====================================================

    return {

        "access_token": token,

        "user": {

            "id": str(db_user.id),

            "full_name": db_user.full_name,

            "email": db_user.email,

            "contact_number":
                db_user.contact_number,

            "alternate_contact_number":
                db_user.alternate_contact_number,

            "role": db_user.role,
        },
    }


# =========================================================
# PROFILE DETAIL
# =========================================================

@router.get("/profile-detail/{user_id}")
def profile_detail(
    user_id: str,

    current_user_id: str = Depends(
        get_current_user_id
    ),

    db: Session = Depends(get_db),
):

    # =====================================================
    # SECURITY
    # User can only access own profile
    # =====================================================

    if str(user_id) != str(current_user_id):

        raise HTTPException(
            status_code=403,
            detail="You are not allowed to access this profile.",
        )

    # =====================================================
    # GET USER
    # =====================================================

    user = (
        db.query(User)
        .filter(
            User.id == current_user_id
        )
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    # =====================================================
    # GET ADDRESS
    # =====================================================

    address = (
        db.query(Address)
        .filter(
            Address.user_id == user.id
        )
        .first()
    )

    # =====================================================
    # ADDRESS RESPONSE
    # =====================================================

    address_data = None

    if address:

        address_data = {

            "id": address.id,

            "address_type":
                address.address_type,

            "flat_house_no":
                address.flat_house_no,

            "address1":
                address.address1,

            "address2":
                address.address2,

            "state":
                address.state,

            "city_village":
                address.city_village,

            "pincode":
                address.pincode,
        }

    # =====================================================
    # RESPONSE
    # =====================================================

    return {

        "message":
            "Profile details fetched successfully",

        "user": {

            "id": str(user.id),

            "full_name":
                user.full_name,

            "email":
                user.email,

            "contact_number":
                user.contact_number,

            "alternate_contact_number":
                user.alternate_contact_number,

            "role":
                user.role,

            "address":
                address_data,
        },
    }


# =========================================================
# UPDATE PROFILE
# =========================================================

@router.put("/profile")
def update_profile(
    data: UpdateProfile,

    current_user_id: str = Depends(
        get_current_user_id
    ),

    db: Session = Depends(get_db),
):

    # =====================================================
    # GET USER
    # =====================================================

    user = (
        db.query(User)
        .filter(
            User.id == current_user_id
        )
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    # =====================================================
    # CHECK EMAIL
    # =====================================================

    existing_user = (
        db.query(User)
        .filter(
            User.email == data.email,
            User.id != current_user_id,
        )
        .first()
    )

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already exists",
        )

    # =====================================================
    # UPDATE USER
    # =====================================================

    user.full_name = data.full_name

    user.email = data.email

    user.contact_number = data.contact_number

    user.alternate_contact_number = (
        data.alternate_contact_number
    )

    # =====================================================
    # GET ADDRESS
    # =====================================================

    address = (
        db.query(Address)
        .filter(
            Address.user_id == user.id
        )
        .first()
    )

    # =====================================================
    # CREATE ADDRESS
    # =====================================================

    if not address:

        address = Address(

            user_id=user.id,

            address_type=
                data.address.address_type,

            flat_house_no=
                data.address.flat_house_no,

            address1=
                data.address.address1,

            address2=
                data.address.address2,

            state=
                data.address.state,

            city_village=
                data.address.city_village,

            pincode=
                data.address.pincode,
        )

        db.add(address)

    # =====================================================
    # UPDATE ADDRESS
    # =====================================================

    else:

        address.address_type = (
            data.address.address_type
        )

        address.flat_house_no = (
            data.address.flat_house_no
        )

        address.address1 = (
            data.address.address1
        )

        address.address2 = (
            data.address.address2
        )

        address.state = (
            data.address.state
        )

        address.city_village = (
            data.address.city_village
        )

        address.pincode = (
            data.address.pincode
        )

    # =====================================================
    # COMMIT
    # =====================================================

    db.commit()

    db.refresh(user)
    db.refresh(address)

    # =====================================================
    # RESPONSE
    # =====================================================

    return {

        "message":
            "Profile Updated Successfully",

        "user": {

            "id": str(user.id),

            "full_name":
                user.full_name,

            "email":
                user.email,

            "contact_number":
                user.contact_number,

            "alternate_contact_number":
                user.alternate_contact_number,

            "role":
                user.role,

            "address": {

                "id":
                    address.id,

                "address_type":
                    address.address_type,

                "flat_house_no":
                    address.flat_house_no,

                "address1":
                    address.address1,

                "address2":
                    address.address2,

                "state":
                    address.state,

                "city_village":
                    address.city_village,

                "pincode":
                    address.pincode,
            },
        },
    }


# =========================================================
# CHANGE PASSWORD
# =========================================================

@router.put("/change-password")
def change_password(
    data: ChangePassword,

    current_user_id: str = Depends(
        get_current_user_id
    ),

    db: Session = Depends(get_db),
):

    # =====================================================
    # GET USER
    # =====================================================

    user = (
        db.query(User)
        .filter(
            User.id == current_user_id
        )
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    # =====================================================
    # VERIFY CURRENT PASSWORD
    # =====================================================

    if not verify_password(
        data.current_password,
        user.password_hash,
    ):

        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect",
        )

    # =====================================================
    # UPDATE PASSWORD
    # =====================================================

    user.password_hash = hash_password(
        data.new_password
    )

    db.commit()

    return {
        "message": "Password Changed Successfully",
    }


# =========================================================
# LOGOUT
# =========================================================

@router.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials =
        Depends(security),

    current_user_id: str = Depends(
        get_current_user_id
    ),

    db: Session = Depends(get_db),
):

    token = credentials.credentials

    # =====================================================
    # DECODE TOKEN
    # =====================================================

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
        )

    # =====================================================
    # GET JTI
    # =====================================================

    jti = payload.get("jti")

    if not jti:

        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
        )

    # =====================================================
    # CHECK EXISTING REVOKED TOKEN
    # =====================================================

    existing_token = (
        db.query(RevokedToken)
        .filter(
            RevokedToken.jti == jti
        )
        .first()
    )

    if not existing_token:

        revoked_token = RevokedToken(

            jti=jti,

            user_id=str(
                current_user_id
            ),
        )

        db.add(revoked_token)

        db.commit()

    return {
        "message": "Logout successful"
    }