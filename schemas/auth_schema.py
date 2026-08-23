from pydantic import BaseModel, EmailStr, Field
from typing import Optional


# =========================================================
# ADDRESS
# =========================================================

class AddressCreate(BaseModel):

    address_type: str = Field(
        ...,
        pattern="^(home|work)$"
    )

    flat_house_no: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    address1: str = Field(
        ...,
        min_length=1,
        max_length=255
    )

    address2: Optional[str] = Field(
        default=None,
        max_length=255
    )

    state: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    city_village: str = Field(
        ...,
        min_length=1,
        max_length=150
    )

    pincode: str = Field(
        ...,
        min_length=6,
        max_length=10
    )


# =========================================================
# SIGNUP
# =========================================================

class UserSignup(BaseModel):

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=150
    )

    email: EmailStr

    contact_number: str = Field(
        ...,
        min_length=10,
        max_length=15
    )

    alternate_contact_number: Optional[str] = Field(
        default=None,
        max_length=15
    )

    password: str = Field(
        ...,
        min_length=6
    )

    address: AddressCreate


# =========================================================
# LOGIN
# =========================================================

class UserLogin(BaseModel):

    email: EmailStr

    password: str


# =========================================================
# UPDATE PROFILE
# =========================================================

class UpdateProfile(BaseModel):

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=150
    )

    email: EmailStr

    contact_number: str = Field(
        ...,
        min_length=10,
        max_length=15
    )

    alternate_contact_number: Optional[str] = Field(
        default=None,
        max_length=15
    )

    address: AddressCreate


# =========================================================
# CHANGE PASSWORD
# =========================================================

class ChangePassword(BaseModel):

    current_password: str

    new_password: str = Field(
        ...,
        min_length=6
    )

# =========================================================
# FORGOT PASSWORD
# =========================================================

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


# =========================================================
# VERIFY FORGOT PASSWORD OTP
# =========================================================

class VerifyForgotPasswordOTP(BaseModel):
    email: EmailStr

    otp: str = Field(
        ...,
        min_length=6,
        max_length=6,
        pattern=r"^[0-9]{6}$"
    )


# =========================================================
# RESET PASSWORD
# =========================================================

class ResetPassword(BaseModel):

    email: EmailStr

    otp: str = Field(
        ...,
        min_length=6,
        max_length=6,
        pattern=r"^[0-9]{6}$"
    )

    new_password: str = Field(
        ...,
        min_length=6
    )