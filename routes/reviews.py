import uuid
from io import BytesIO
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from PIL import Image
from sqlalchemy.orm import Session

from utils.database import get_db
from utils.jwt_handler import get_current_user

from models.review import Review
from models.product import Product
from models.user import User

from schemas.review import (
    ReviewListResponse,
    ReviewResponse,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"],
)


# ============================================================
# REVIEW IMAGE DIRECTORY
# ============================================================

REVIEW_UPLOAD_DIR = Path("attachments/reviews")

REVIEW_UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# IMAGE SETTINGS
# ============================================================

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

MAX_IMAGE_SIZE = 5 * 1024 * 1024


# ============================================================
# CREATE REVIEW
# POST /reviews
# ============================================================

@router.post(
    "",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_review(
    product_id: int = Form(...),
    rating: int = Form(...),
    title: str = Form(...),
    content: str = Form(...),
    image: UploadFile | None = File(None),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user),
):

    # ========================================================
    # RATING
    # ========================================================

    if rating < 1 or rating > 5:
        raise HTTPException(
            status_code=400,
            detail="Rating must be between 1 and 5.",
        )

    # ========================================================
    # TITLE
    # ========================================================

    title = title.strip()

    if not title:
        raise HTTPException(
            status_code=400,
            detail="Review title is required.",
        )

    if len(title) > 200:
        raise HTTPException(
            status_code=400,
            detail="Review title cannot exceed 200 characters.",
        )

    # ========================================================
    # CONTENT
    # ========================================================

    content = content.strip()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Review content is required.",
        )

    # ========================================================
    # PRODUCT
    # ========================================================

    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found.",
        )

    # ========================================================
    # CUSTOMER NAME
    # ========================================================

    customer_name = (
        current_user.full_name.strip()
        if current_user.full_name
        else "Customer"
    )

    # ========================================================
    # IMAGE
    # ========================================================

    image_path = None

    if image:

        # ----------------------------------------------------
        # MIME TYPE
        # ----------------------------------------------------

        if image.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Only JPG, PNG and WEBP images are allowed.",
            )

        # ----------------------------------------------------
        # READ FILE
        # ----------------------------------------------------

        file_data = await image.read()

        # ----------------------------------------------------
        # SIZE
        # ----------------------------------------------------

        if len(file_data) > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail="Image size cannot exceed 5 MB.",
            )

        # ----------------------------------------------------
        # VERIFY IMAGE
        # ----------------------------------------------------

        try:
            img = Image.open(
                BytesIO(file_data)
            )

            img.verify()

        except Exception:

            raise HTTPException(
                status_code=400,
                detail="Uploaded file is not a valid image.",
            )

        # ----------------------------------------------------
        # FILENAME
        # ----------------------------------------------------

        extension = ALLOWED_IMAGE_TYPES[
            image.content_type
        ]

        filename = (
            f"{uuid.uuid4().hex}{extension}"
        )

        file_location = (
            REVIEW_UPLOAD_DIR / filename
        )

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        with open(
            file_location,
            "wb",
        ) as file:

            file.write(file_data)

        # ----------------------------------------------------
        # DATABASE PATH
        # ----------------------------------------------------

        image_path = (
            f"/attachments/reviews/{filename}"
        )

    # ========================================================
    # CREATE REVIEW
    # ========================================================

    review = Review(
        product_id=product_id,
        user_id=current_user.id,

        customer_name=customer_name,

        rating=rating,
        title=title,
        content=content,

        image=image_path,

        # Do not automatically verify here.
        # Set this to True only when your purchase
        # verification logic confirms the order.
        is_verified=False,

        is_active=True,
    )

    db.add(review)

    db.commit()

    db.refresh(review)

    # ========================================================
    # RETURN PUBLIC REVIEW
    # ========================================================

    return {
        "id": review.id,
        "rating": review.rating,
        "title": review.title,
        "content": review.content,
        "image": review.image,
        "customer_name": review.customer_name,
        "is_verified": review.is_verified,
        "created_at": review.created_at,
        "product_name": product.name,
        "product_image": product.image,
    }


# ============================================================
# GET PRODUCT REVIEWS
# GET /reviews/product/{product_id}
# ============================================================

@router.get(
    "/product/{product_id}",
    response_model=ReviewListResponse,
)
def get_product_reviews(
    product_id: int,
    db: Session = Depends(get_db),
):

    # ========================================================
    # PRODUCT
    # ========================================================

    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found.",
        )

    # ========================================================
    # REVIEWS
    # ========================================================

    reviews = (
        db.query(Review)
        .filter(
            Review.product_id == product_id,
            Review.is_active.is_(True),
        )
        .order_by(
            Review.created_at.desc()
        )
        .all()
    )

    # ========================================================
    # AVERAGE
    # ========================================================

    total = len(reviews)

    if total:

        average_rating = round(
            sum(
                review.rating
                for review in reviews
            ) / total,
            1,
        )

    else:

        average_rating = 0.0

    # ========================================================
    # PUBLIC REVIEW LIST
    # ========================================================

    review_list = []

    for review in reviews:

        review_list.append(
            {
                "id": review.id,

                "rating": review.rating,

                "title": review.title,

                "content": review.content,

                "image": review.image,

                "customer_name": review.customer_name,

                "is_verified": review.is_verified,

                "created_at": review.created_at,

                "product_name": product.name,

                "product_image": product.image,
            }
        )

    # ========================================================
    # RESPONSE
    # ========================================================

    return {
        "total": total,

        "average_rating": average_rating,

        "reviews": review_list,
    }