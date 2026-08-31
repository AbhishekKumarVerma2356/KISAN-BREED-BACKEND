from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from utils.database import get_db
from models.product import Product
from models.review import Review
from schemas.product_schema import ProductResponse


router = APIRouter(
    tags=["Products"]
)


# =========================================================
# HELPER FUNCTION
# GET PRODUCT REVIEW INFORMATION
# =========================================================

def get_product_review_data(
    db: Session,
    product_id: int
):
    """
    Get average rating and review count for a product.

    Only active reviews are considered.
    """

    review_data = (
        db.query(
            func.coalesce(
                func.avg(Review.rating),
                0
            ).label("avg_review"),

            func.count(
                Review.id
            ).label("review_count")
        )
        .filter(
            Review.product_id == product_id,
            Review.is_active.is_(True)
        )
        .first()
    )

    avg_review = float(
        review_data.avg_review or 0
    )

    review_count = int(
        review_data.review_count or 0
    )

    return avg_review, review_count


# =========================================================
# GET ALL PRODUCTS
# =========================================================

@router.get(
    "/products",
    response_model=list[ProductResponse]
)
def get_products(
    db: Session = Depends(get_db)
):

    products = (
        db.query(Product)
        .all()
    )

    result = []

    for item in products:

        # -------------------------------------------------
        # REVIEW DATA
        # -------------------------------------------------

        avg_review, review_count = (
            get_product_review_data(
                db,
                item.id
            )
        )

        # -------------------------------------------------
        # PRODUCT RESPONSE
        # -------------------------------------------------

        result.append({

            "id": item.id,

            "name": item.name,

            "slug": item.slug,

            "category": item.category,

            "short_description": (
                item.short_description
                if item.short_description
                else None
            ),

            "description": (
                item.description
                if item.description
                else None
            ),

            # -------------------------------------------------
            # PRICE
            # -------------------------------------------------

            "price": (
                float(item.price)
                if item.price is not None
                else 0
            ),

            # -------------------------------------------------
            # DISCOUNT
            # Taken directly from products table
            # -------------------------------------------------

            "discount": (
                float(item.discount)
                if item.discount is not None
                else 0
            ),

            # -------------------------------------------------
            # IMAGE
            # -------------------------------------------------

            "image": (
                f"http://localhost:8000/"
                f"attachments/products/"
                f"{item.image}"
                if item.image
                else None
            ),

            # -------------------------------------------------
            # QUANTITY
            # -------------------------------------------------

            "quantity": (
                float(item.quantity)
                if item.quantity is not None
                else 1
            ),

            # -------------------------------------------------
            # UNIT OF MEASURE
            # -------------------------------------------------

            "unitOfMeasure": (
                item.unit_of_measure
                if item.unit_of_measure
                else "piece"
            ),

            # -------------------------------------------------
            # REVIEW INFORMATION
            # -------------------------------------------------

            "avgReview": round(
                avg_review,
                2
            ),

            "reviewCount": review_count
        })

    return result


# =========================================================
# GET PRODUCT BY SLUG
# =========================================================

@router.get(
    "/products/{slug}",
    response_model=ProductResponse
)
def get_product(
    slug: str,
    db: Session = Depends(get_db)
):

    # -------------------------------------------------
    # FIND PRODUCT
    # -------------------------------------------------

    product = (
        db.query(Product)
        .filter(
            Product.slug == slug
        )
        .first()
    )

    # -------------------------------------------------
    # PRODUCT NOT FOUND
    # -------------------------------------------------

    if not product:

        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # -------------------------------------------------
    # REVIEW DATA
    # -------------------------------------------------

    avg_review, review_count = (
        get_product_review_data(
            db,
            product.id
        )
    )

    # -------------------------------------------------
    # RESPONSE
    # -------------------------------------------------

    return {

        "id": product.id,

        "name": product.name,

        "slug": product.slug,

        "category": product.category,

        "short_description": (
            product.short_description
            if product.short_description
            else None
        ),

        "description": (
            product.description
            if product.description
            else None
        ),

        # -------------------------------------------------
        # PRICE
        # -------------------------------------------------

        "price": (
            float(product.price)
            if product.price is not None
            else 0
        ),

        # -------------------------------------------------
        # DISCOUNT
        # From products table
        # -------------------------------------------------

        "discount": (
            float(product.discount)
            if product.discount is not None
            else 0
        ),

        # -------------------------------------------------
        # IMAGE
        # -------------------------------------------------

        "image": (
            f"http://localhost:8000/"
            f"attachments/products/"
            f"{product.image}"
            if product.image
            else None
        ),

        # -------------------------------------------------
        # QUANTITY
        # -------------------------------------------------

        "quantity": (
            float(product.quantity)
            if product.quantity is not None
            else 1
        ),

        # -------------------------------------------------
        # UNIT OF MEASURE
        # -------------------------------------------------

        "unitOfMeasure": (
            product.unit_of_measure
            if product.unit_of_measure
            else "piece"
        ),

        # -------------------------------------------------
        # REVIEW INFORMATION
        # -------------------------------------------------

        "avgReview": round(
            avg_review,
            2
        ),

        "reviewCount": review_count
    }