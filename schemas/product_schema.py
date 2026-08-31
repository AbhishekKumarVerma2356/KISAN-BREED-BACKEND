from pydantic import BaseModel, ConfigDict, Field


class ProductResponse(BaseModel):

    id: int
    name: str
    slug: str
    category: str

    # Optional product description
    short_description: str | None = None
    description: str | None = None

    price: float
    discount: float = 0

    image: str | None = None

    # Quantity
    quantity: float = 1

    # Unit of measure
    unit_of_measure: str = "piece"

    # Review information
    avg_review: float = 0
    review_count: int = 0

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )