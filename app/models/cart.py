import strawberry
from sqlalchemy import Column, ForeignKey, Integer, Numeric
from typing_extensions import Self

from app.models.base import Base


class CartItem(Base):
    __tablename__ = "cart_items"
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    product_id = Column(ForeignKey("products.id", ondelete="CASCADE"), primary_key=True)
    quantity = Column(Integer)
    price = Column(Numeric)


@strawberry.type
class CartItemType:
    user_id: str
    product_id: str
    quantity: int
    price: float

    @classmethod
    def parse_type(cls, cart_item: CartItem) -> Self:
        return CartItemType(user_id=str(cart_item.user_id),
                            product_id=str(cart_item.product_id),
                            quantity=cart_item.quantity,
                            price=cart_item.price)
