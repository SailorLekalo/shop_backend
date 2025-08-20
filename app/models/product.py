from sqlalchemy import UUID, Numeric, Column, String
import strawberry
import uuid

from app.models.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(50))
    description = Column(String(10000))
    price = Column(Numeric)
    amount = Column(Numeric)


@strawberry.type
class ProductType:
    id: str
    name: str
    description: str
    price: float
    amount: int

    @classmethod
    def parseType(cls, product: Product):
        return ProductType(id=str(product.id),
                           name=product.name,
                           description=product.description,
                           price=product.price,
                           amount=product.amount)
