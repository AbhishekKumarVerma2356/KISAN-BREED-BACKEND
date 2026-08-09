from pydantic import BaseModel


class AddCart(BaseModel):
    user_id: int
    product_id: int
    quantity: int = 1


class UpdateCart(BaseModel):
    quantity: int