from sqlalchemy import Column, Integer, String, Float, Text
from utils.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False)
    category = Column(String(100))
    short_description = Column(Text)
    description = Column(Text)
    price = Column(Float)
    image = Column(String(255))