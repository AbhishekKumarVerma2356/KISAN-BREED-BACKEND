from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from utils.database import get_db
from models.product import Product
from models.review import Review


router = APIRouter(
    tags=["Products"]
)


# =========================================================
# HELPER FUNCTION
# =========================================================

def get_product_review_data(
    db: Session,
    product_id: int
):
    """
    Get average rating and review count
    for a product.

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

@router.get("/products")
def get_products(
    db: Session = Depends(get_db)
):
    products = (
        db.query(Product)
        .all()
    )

    result = []

    for item in products:

        avg_review, review_count = (
            get_product_review_data(
                db,
                item.id
            )
        )

        result.append(
            {
                "id": item.id,

                "name": item.name,

                "slug": item.slug,

                "category": item.category,

                "shortDescription": (
                    item.short_description
                ),

                "description": (
                    item.description
                ),

                "price": (
                    float(item.price)
                    if item.price is not None
                    else 0
                ),

                "discount": (
                    float(item.discount)
                    if item.discount is not None
                    else 0
                ),

                "quantity": (
                    float(item.quantity)
                    if item.quantity is not None
                    else 1
                ),

                "unitOfMeasure": (
                    item.unit_of_measure
                    or "piece"
                ),

                "avgReview": round(
                    avg_review,
                    2
                ),

                "reviewCount": review_count,

                "image": (
                    f"http://localhost:8000/"
                    f"attachments/products/"
                    f"{item.image}"
                    if item.image
                    else None
                )
            }
        )

    return result


# =========================================================
# GET PRODUCT BY SLUG
# =========================================================

@router.get("/products/{slug}")
def get_product(
    slug: str,
    db: Session = Depends(get_db)
):

    product = (
        db.query(Product)
        .filter(
            Product.slug == slug
        )
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # =====================================================
    # GET REVIEW INFORMATION
    # =====================================================

    avg_review, review_count = (
        get_product_review_data(
            db,
            product.id
        )
    )

    # =====================================================
    # RESPONSE
    # =====================================================

    return {
        "id": product.id,

        "name": product.name,

        "slug": product.slug,

        "category": product.category,

        "shortDescription": (
            product.short_description
        ),

        "description": (
            product.description
        ),

        "price": (
            float(product.price)
            if product.price is not None
            else 0
        ),

        "discount": (
            float(product.discount)
            if product.discount is not None
            else 0
        ),

        "quantity": (
            float(product.quantity)
            if product.quantity is not None
            else 1
        ),

        "unitOfMeasure": (
            product.unit_of_measure
            or "piece"
        ),

        "avgReview": round(
            avg_review,
            2
        ),

        "reviewCount": review_count,

        "image": (
            f"http://localhost:8000/"
            f"attachments/products/"
            f"{product.image}"
            if product.image
            else None
        )
    }