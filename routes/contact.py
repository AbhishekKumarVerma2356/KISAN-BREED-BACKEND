from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from utils.database import get_db

from models.contact_message import ContactMessage

from schemas.contact_schema import ContactCreate


router = APIRouter(
    prefix="/contact",
    tags=["Contact"]
)


# =========================================================
# CREATE CONTACT MESSAGE
# =========================================================

@router.post(
    "",
    status_code=status.HTTP_201_CREATED
)
def create_contact_message(
    data: ContactCreate,
    db: Session = Depends(get_db)
):

    try:

        # -----------------------------------------
        # Clean input
        # -----------------------------------------

        name = data.name.strip()
        phone = data.phone.strip()
        email = str(data.email).strip().lower()
        message = data.message.strip()

        # -----------------------------------------
        # Required validation
        # -----------------------------------------

        if not name:
            raise HTTPException(
                status_code=400,
                detail="Name is required."
            )

        if not phone:
            raise HTTPException(
                status_code=400,
                detail="Phone number is required."
            )

        if not email:
            raise HTTPException(
                status_code=400,
                detail="Email is required."
            )

        if not message:
            raise HTTPException(
                status_code=400,
                detail="Message is required."
            )

        # -----------------------------------------
        # Phone validation
        # -----------------------------------------

        if not phone.isdigit():

            raise HTTPException(
                status_code=400,
                detail="Phone number must contain only digits."
            )

        if len(phone) < 10 or len(phone) > 15:

            raise HTTPException(
                status_code=400,
                detail="Please enter a valid phone number."
            )

        # -----------------------------------------
        # Create message
        # -----------------------------------------

        contact_message = ContactMessage(
            name=name,
            phone=phone,
            email=email,
            message=message
        )

        db.add(contact_message)

        db.commit()

        db.refresh(contact_message)

        # -----------------------------------------
        # Response
        # -----------------------------------------

        return {
            "success": True,
            "message": "Your message has been submitted successfully.",
            "data": {
                "id": contact_message.id,
                "name": contact_message.name,
                "phone": contact_message.phone,
                "email": contact_message.email,
                "message": contact_message.message,
                "created_at": contact_message.created_at
            }
        }

    except HTTPException:
        raise

    except SQLAlchemyError as e:

        db.rollback()

        print("Database Error:", e)

        raise HTTPException(
            status_code=500,
            detail="Database error. Please try again later."
        )

    except Exception as e:

        db.rollback()

        print("Contact API Error:", e)

        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again later."
        )


# =========================================================
# GET ALL CONTACT MESSAGES
# Useful later for ADMIN
# =========================================================

@router.get("")
def get_contact_messages(
    db: Session = Depends(get_db)
):

    try:

        messages = (
            db.query(ContactMessage)
            .order_by(ContactMessage.created_at.desc())
            .all()
        )

        result = []

        for item in messages:

            result.append({
                "id": item.id,
                "name": item.name,
                "phone": item.phone,
                "email": item.email,
                "message": item.message,
                "created_at": item.created_at
            })

        return {
            "success": True,
            "data": result
        }

    except SQLAlchemyError as e:

        print("Database Error:", e)

        raise HTTPException(
            status_code=500,
            detail="Unable to fetch contact messages."
        )

    except Exception as e:

        print("Contact API Error:", e)

        raise HTTPException(
            status_code=500,
            detail="Something went wrong."
        )