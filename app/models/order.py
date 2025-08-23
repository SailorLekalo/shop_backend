import enum
import uuid

import strawberry
from sqlalchemy import UUID, Column, Enum, ForeignKey, Numeric, select
from strawberry import Info
from typing_extensions import Self

from app.models.base import Base


@strawberry.enum
class OrderStatusEnum(str, enum.Enum):
    IN_PROCESS = "In process"
    PAID = "Paid"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"
    CANCELED = "Canceled"


class Order(Base):
    __tablename__ = "orders"

    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"))
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    status = Column(Enum(OrderStatusEnum, name="order_status"), default=OrderStatusEnum.IN_PROCESS)
    price = Column(Numeric)


class OrderItem(Base):
    __tablename__ = "order_items"

    self_id = Column(UUID, primary_key=True, default=uuid.uuid4)
    order_id = Column(ForeignKey("orders.id"))
    product_id = Column(ForeignKey("products.id"))
    quantity = Column(Numeric)
    price = Column(Numeric)


@strawberry.type
class OrderItemType:
    self_id: str
    order_id: str
    product_id: str
    quantity: float
    price: float

    @classmethod
    def parse_type(cls, order_item: OrderItem) -> Self:
        return OrderItemType(
            self_id=str(order_item.self_id),
            order_id=str(order_item.order_id),
            product_id=str(order_item.product_id),
            quantity=float(order_item.quantity),
            price=float(order_item.price),
        )


@strawberry.type
class OrderType:
    user_id: str
    id: str
    status: str
    items: list[OrderItemType]
    price: float

    @classmethod
    async def parse_type(cls, order: Order, info: Info) -> Self:
        db = info.context["db"]
        result = await db.execute(
            select(OrderItem).where(OrderItem.order_id == order.id),
        )
        result = result.scalar()
        items = [result] if isinstance(result, OrderItem) else result.all()
        return OrderType(
            user_id=str(order.user_id),
            id=str(order.id),
            status=order.status,
            price=order.price,
            items=[OrderItemType.parse_type(item) for item in items],
        )
