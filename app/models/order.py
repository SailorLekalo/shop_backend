import enum
import uuid

import strawberry
from sqlalchemy import UUID, Column, Enum, ForeignKey, Numeric, select
from strawberry import Info
from typing_extensions import Self

from app.models.base import Base
from app.models.product import Product, ProductType


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
class OrderType:
    user_id: str
    id: str
    status: str
    price: float

    @strawberry.field
    async def products(self, info: Info) -> list[ProductType]:
        db = info.context["db"]

        result = await db.execute(
            select(OrderItem, Product)
            .join(Product, Product.id == OrderItem.product_id)
            .where(OrderItem.order_id == self.id),
        )
        rows = result.all()

        return [
            ProductType.parse_type(prod, quantity=item.quantity)
            for item, prod in rows
        ]
    @classmethod
    async def parse_type(cls, order: Order) -> Self:
        return OrderType(
            user_id=str(order.user_id),
            id=str(order.id),
            status=order.status.value,
            price=float(order.price),
        )
