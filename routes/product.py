from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from utils.database import get_db

from models.product import Product

router = APIRouter(tags=["Products"])


@router.get("/products")
def get_products(db: Session = Depends(get_db)):

    products = db.query(Product).all()

    result = []

    for item in products:

        result.append(
            {
                "id": item.id,
                "name": item.name,
                "slug": item.slug,
                "category": item.category,
                "shortDescription": item.short_description,
                "description": item.description,
                "price": item.price,
                "image": f"http://localhost:8000/attachments/products/{item.image}"
            }
        )

    return result

@router.get("/products/{slug}")
def get_product(slug: str, db: Session = Depends(get_db)):

    product = (
        db.query(Product)
        .filter(Product.slug == slug)
        .first()
    )

    if not product:
        return None

    return {
        "id": product.id,
        "name": product.name,
        "slug": product.slug,
        "category": product.category,
        "shortDescription": product.short_description,
        "description": product.description,
        "price": product.price,
        "image": f"http://localhost:8000/attachments/products/{product.image}"
    }

