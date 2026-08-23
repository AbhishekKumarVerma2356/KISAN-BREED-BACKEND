from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ============================================================
# REVIEW RESPONSE
# ============================================================

class ReviewResponse(BaseModel):

    id: int

    rating: int

    title: str

    content: str

    image: str | None = None

    customer_name: str

    is_verified: bool

    created_at: datetime

    product_name: str | None = None

    product_image: str | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# REVIEW LIST RESPONSE
# ============================================================

class ReviewListResponse(BaseModel):

    total: int

    average_rating: float

    reviews: list[ReviewResponse]