from pydantic import BaseModel
from uuid import UUID


class AddCart(BaseModel):
    user_id: UUID
    product_id: int
    quantity: int = 1


class UpdateCart(BaseModel):
    quantity: int