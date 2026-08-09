import os
import shutil
import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
)

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from slugify import slugify

from utils.database import get_db
from models.product import Product

router = APIRouter(
    prefix="/admin/products",
    tags=["Admin Products"]
)

# -----------------------------
# Upload Folder
# -----------------------------

UPLOAD_FOLDER = os.path.join("attachments", "products")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

BASE_IMAGE_URL = "http://localhost:8000/attachments/products"


# -----------------------------
# Get All Products
# -----------------------------

@router.get("")
def get_products(db: Session = Depends(get_db)):
    try:

        products = db.query(Product).all()

        return [
            {
                "id": p.id,
                "name": p.name,
                "slug": p.slug,
                "category": p.category,
                "short_description": p.short_description,
                "description": p.description,
                "price": p.price,
                "image": f"{BASE_IMAGE_URL}/{p.image}" if p.image else None,
            }
            for p in products
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# -----------------------------
# Get Product By ID
# -----------------------------

@router.get("/{id}")
def get_product(
    id: int,
    db: Session = Depends(get_db)
):

    try:

        product = (
            db.query(Product)
            .filter(Product.id == id)
            .first()
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        return {
            "id": product.id,
            "name": product.name,
            "slug": product.slug,
            "category": product.category,
            "short_description": product.short_description,
            "description": product.description,
            "price": product.price,
            "image": f"{BASE_IMAGE_URL}/{product.image}" if product.image else None,
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# -----------------------------
# Add Product
# -----------------------------

@router.post("")
def add_product(

    name: str = Form(...),
    category: str = Form(...),
    short_description: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    image: UploadFile = File(...),

    db: Session = Depends(get_db)

):

    try:

        slug = slugify(name)

        existing = (
            db.query(Product)
            .filter(Product.slug == slug)
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Product already exists."
            )

        extension = os.path.splitext(image.filename)[1]

        filename = f"{uuid.uuid4()}{extension}"

        filepath = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        product = Product(
            name=name,
            slug=slug,
            category=category,
            short_description=short_description,
            description=description,
            price=price,
            image=filename
        )

        db.add(product)
        db.commit()
        db.refresh(product)

        return {
            "success": True,
            "message": "Product added successfully",
            "product": {
                "id": product.id,
                "name": product.name,
                "image": f"{BASE_IMAGE_URL}/{filename}"
            }
        }

    except HTTPException:
        raise

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Database error."
        )

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# -----------------------------
# Update Product
# -----------------------------

@router.put("/{id}")
def update_product(

    id: int,

    name: str = Form(...),
    category: str = Form(...),
    short_description: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),

    image: UploadFile | None = File(None),

    db: Session = Depends(get_db)

):

    try:

        product = (
            db.query(Product)
            .filter(Product.id == id)
            .first()
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found."
            )

        slug = slugify(name)

        duplicate = (
            db.query(Product)
            .filter(
                Product.slug == slug,
                Product.id != id
            )
            .first()
        )

        if duplicate:
            raise HTTPException(
                status_code=400,
                detail="Product already exists."
            )

        product.name = name
        product.slug = slug
        product.category = category
        product.short_description = short_description
        product.description = description
        product.price = price

        if image:

            if product.image:

                old_image = os.path.join(
                    UPLOAD_FOLDER,
                    product.image
                )

                if os.path.exists(old_image):
                    os.remove(old_image)

            extension = os.path.splitext(image.filename)[1]

            filename = f"{uuid.uuid4()}{extension}"

            filepath = os.path.join(
                UPLOAD_FOLDER,
                filename
            )

            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

            product.image = filename

        db.commit()
        db.refresh(product)

        return {
            "success": True,
            "message": "Product updated successfully",
            "product": {
                "id": product.id,
                "image": f"{BASE_IMAGE_URL}/{product.image}"
            }
        }

    except HTTPException:
        raise

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Database error."
        )

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# -----------------------------
# Delete Product
# -----------------------------

@router.delete("/{id}")
def delete_product(
    id: int,
    db: Session = Depends(get_db)
):

    try:

        product = (
            db.query(Product)
            .filter(Product.id == id)
            .first()
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found."
            )

        if product.image:

            image_path = os.path.join(
                UPLOAD_FOLDER,
                product.image
            )

            if os.path.exists(image_path):
                os.remove(image_path)

        db.delete(product)
        db.commit()

        return {
            "success": True,
            "message": "Product deleted successfully"
        }

    except HTTPException:
        raise

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Database error."
        )

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )                                                                  