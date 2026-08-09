from pydantic import BaseModel


class ProductResponse(BaseModel):
    id: int
    name: str
    slug: str
    category: str
    short_description: str
    description: str
    price: float
    image: str

    class Config:
        from_attributes = True