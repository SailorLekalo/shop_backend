import strawberry
from sqlalchemy import Column, ForeignKey, Integer, Numeric
from typing_extensions import Self

from app.models.base import Base
from app.models.product import Product, ProductType


class CartItem(Base):
    __tablename__ = "cart_items"
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    product_id = Column(ForeignKey("products.id", ondelete="CASCADE"), primary_key=True)
    quantity = Column(Integer)
    price = Column(Numeric)


@strawberry.type
class CartItemType:
    user_id: str
    product: ProductType
    quantity: int
    price: float

    @classmethod
    def parse_type(cls, cart_item: CartItem, product: Product) -> Self:
        return CartItemType(
            user_id=str(cart_item.user_id),
            product=ProductType.parse_type(product, quantity=cart_item.quantity),
            quantity=cart_item.quantity,
            price=float(cart_item.price),
        )
