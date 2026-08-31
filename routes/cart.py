from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from utils.database import get_db
from models.cart import Cart
from models.product import Product
from schemas.cart_schema import AddCart, UpdateCart

router = APIRouter(tags=["Cart"])


# =========================================================
# ADD TO CART
# =========================================================

@router.post("/cart")
def add_to_cart(
    data: AddCart,
    db: Session = Depends(get_db)
):
    # Check whether product exists
    product = (
        db.query(Product)
        .filter(Product.id == data.product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # Prevent Coming Soon products from being added
    if (
        product.category
        and product.category.lower() == "coming soon"
    ):
        raise HTTPException(
            status_code=400,
            detail="This product is coming soon"
        )

    # Validate quantity
    if data.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0"
        )

    # Check existing cart item
    cart = (
        db.query(Cart)
        .filter(
            Cart.user_id == data.user_id,
            Cart.product_id == data.product_id
        )
        .first()
    )

    if cart:
        cart.quantity += data.quantity
    else:
        cart = Cart(
            user_id=data.user_id,
            product_id=data.product_id,
            quantity=data.quantity
        )

        db.add(cart)

    db.commit()
    db.refresh(cart)

    return {
        "message": "Added to cart",
        "cart_id": cart.id,
        "quantity": cart.quantity
    }


# =========================================================
# GET CART
# =========================================================

@router.get("/cart/{user_id}")
def get_cart(
    user_id: UUID,
    db: Session = Depends(get_db)
):

    carts = (
        db.query(Cart)
        .filter(Cart.user_id == user_id)
        .all()
    )

    result = []

    for cart in carts:

        # Get product
        product = (
            db.query(Product)
            .filter(Product.id == cart.product_id)
            .first()
        )

        if not product:
            continue

        # -------------------------------------------------
        # PRODUCT PRICE
        # -------------------------------------------------

        price = float(
            product.price
            if product.price is not None
            else 0
        )

        # -------------------------------------------------
        # PRODUCT DISCOUNT
        # -------------------------------------------------

        discount = float(
            product.discount
            if product.discount is not None
            else 0
        )

        # -------------------------------------------------
        # DISCOUNTED UNIT PRICE
        # -------------------------------------------------

        discounted_price = (
            price - (price * discount / 100)
        )

        # -------------------------------------------------
        # CART QUANTITY
        # -------------------------------------------------

        cart_quantity = int(
            cart.quantity
            if cart.quantity is not None
            else 1
        )

        # -------------------------------------------------
        # ITEM TOTAL
        # -------------------------------------------------

        item_total = (
            discounted_price * cart_quantity
        )

        # -------------------------------------------------
        # PRODUCT PACK QUANTITY
        # Example:
        # 1000 ML
        # 1 KG
        # 500 GM
        # -------------------------------------------------

        product_quantity = float(
            product.quantity
            if product.quantity is not None
            else 1
        )

        # -------------------------------------------------
        # UNIT OF MEASURE
        # -------------------------------------------------

        unit_of_measure = (
            product.unit_of_measure
            if product.unit_of_measure
            else "piece"
        )

        # -------------------------------------------------
        # IMAGE
        # -------------------------------------------------

        image = (
            f"http://localhost:8000/attachments/products/"
            f"{product.image}"
            if product.image
            else None
        )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        result.append({

            # Cart ID
            "id": cart.id,

            # Product ID
            "product_id": product.id,

            # Product name
            "name": product.name,

            # Original price
            "price": round(price, 2),

            # Discount percentage
            "discount": round(discount, 2),

            # Discounted price per pack
            "discountedPrice": round(
                discounted_price,
                2
            ),

            # Product pack quantity
            # Example: 1000 ML
            "product_quantity": product_quantity,

            # Unit
            # Example: ML / KG / piece
            "unitOfMeasure": unit_of_measure,

            # Quantity added to cart
            # Example: 2 packs
            "cart_quantity": cart_quantity,

            # Total for this cart item
            "itemTotal": round(
                item_total,
                2
            ),

            # Product image
            "image": image
        })

    return result


# =========================================================
# UPDATE CART
# =========================================================

@router.put("/cart/{cart_id}")
def update_cart(
    cart_id: int,
    data: UpdateCart,
    db: Session = Depends(get_db)
):

    if data.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0"
        )

    cart = (
        db.query(Cart)
        .filter(Cart.id == cart_id)
        .first()
    )

    if not cart:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    cart.quantity = data.quantity

    db.commit()
    db.refresh(cart)

    return {
        "message": "Cart Updated",
        "cart_id": cart.id,
        "quantity": cart.quantity
    }


# =========================================================
# DELETE CART
# =========================================================

@router.delete("/cart/{cart_id}")
def delete_cart(
    cart_id: int,
    db: Session = Depends(get_db)
):

    cart = (
        db.query(Cart)
        .filter(Cart.id == cart_id)
        .first()
    )

    if not cart:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    db.delete(cart)
    db.commit()

    return {
        "message": "Removed Successfully"
    }