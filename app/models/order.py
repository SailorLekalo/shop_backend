import strawberry
from sqlalchemy import UUID, Numeric, Column, ForeignKey, String
import uuid

from app.models.base import Base


class Order(Base):
    __tablename__ = "orders"

    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"))
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    status = Column(String(30))
    price = Column(Numeric)


class OrderItem(Base):
    __tablename__ = "order_items"

    self_id = Column(UUID, primary_key=True, default=uuid.uuid4)
    order_id = Column(ForeignKey("orders.id"))
    product_id = Column(ForeignKey("products.id"))
    quantity = Column(Numeric)
    price = Column(Numeric)


@strawberry.type
class OrderType:
    user_id: str
    id: str
    status: str
    price: float

    @classmethod
    def parseType(cls, order: Order):
        return OrderType(
            user_id=str(order.user_id),
            id=str(order.id),
            status=order.status,
            price=order.price
        )


@strawberry.type
class OrderItemType:
    self_id: str
    order_id: str
    product_id: str
    quantity: float
    price: float

    @classmethod
    def parseType(cls, order_item: OrderItem):
        return OrderItemType(
            self_id=str(order_item.self_id),
            order_id=str(order_item.order_id),
            product_id=str(order_item.product_id),
            quantity=float(order_item.quantity),
            price=float(order_item.price)
        )
