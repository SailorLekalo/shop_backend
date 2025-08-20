import strawberry
from sqlalchemy import Integer, Column, ForeignKey

from app.models.base import Base


class CartItem(Base):
    __tablename__ = "cart_items"
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    product_id = Column(ForeignKey("products.id", ondelete="CASCADE"), primary_key=True)
    quantity = Column(Integer)


@strawberry.type
class CartItemType:
    user_id: str
    product_id: str
    quantity: int

    @classmethod
    def parseType(cls, cart_item: CartItem):
        return CartItemType(user_id=str(cart_item.user_id),
                            product_id=str(cart_item.product_id),
                            quantity=cart_item.quantity)
