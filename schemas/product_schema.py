from pydantic import BaseModel


class ProductResponse(BaseModel):
    id: int

    name: str

    slug: str

    category: str

    short_description: str

    description: str

    price: float

    discount: float = 0

    image: str

    # =========================================================
    # QUANTITY
    # =========================================================

    quantity: float

    # =========================================================
    # UNIT OF MEASURE
    # =========================================================

    unit_of_measure: str

    # =========================================================
    # REVIEW INFORMATION
    # =========================================================

    avg_review: float = 0

    review_count: int = 0

    class Config:
        from_attributes = True