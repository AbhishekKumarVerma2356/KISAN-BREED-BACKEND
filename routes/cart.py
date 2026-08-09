from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from utils.database import get_db

from models.cart import Cart
from models.product import Product

from schemas.cart_schema import AddCart, UpdateCart

router = APIRouter(tags=["Cart"])

@router.post("/cart")
def add_to_cart(
    data: AddCart,
    db: Session = Depends(get_db)
):

    cart = db.query(Cart).filter(
        Cart.user_id == data.user_id,
        Cart.product_id == data.product_id
    ).first()

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

    return {
        "message": "Added to cart"
    }

@router.get("/cart/{user_id}")
def get_cart(
    user_id: int,
    db: Session = Depends(get_db)
):

    carts = (
        db.query(Cart)
        .filter(Cart.user_id == user_id)
        .all()
    )

    result = []

    for cart in carts:

        product = (
            db.query(Product)
            .filter(Product.id == cart.product_id)
            .first()
        )

        result.append({

            "id": cart.id,

            "product_id": product.id,

            "name": product.name,

            "price": product.price,

            "quantity": cart.quantity,

            "image": f"http://127.0.0.1:8000/attachments/{product.image}"

        })

    return result

@router.put("/cart/{cart_id}")
def update_cart(
    cart_id: int,
    data: UpdateCart,
    db: Session = Depends(get_db)
):

    cart = db.query(Cart).filter(Cart.id == cart_id).first()

    if not cart:
        raise HTTPException(404, "Cart item not found")

    cart.quantity = data.quantity

    db.commit()

    return {
        "message": "Cart Updated"
    }

@router.delete("/cart/{cart_id}")
def delete_cart(
    cart_id: int,
    db: Session = Depends(get_db)
):

    cart = db.query(Cart).filter(Cart.id == cart_id).first()

    if not cart:
        raise HTTPException(404, "Item not found")

    db.delete(cart)

    db.commit()

    return {
        "message": "Removed Successfully"
    }