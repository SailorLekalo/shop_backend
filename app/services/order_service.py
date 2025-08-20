import strawberry
from sqlalchemy import select

from app.db.db_session import AsyncSessionLocal
from app.models.order import OrderItemType, OrderItem, OrderType, Order
from app.models.user import User


@strawberry.type
class OrderError:
    message: str


@strawberry.type
class OrderItemError:
    message: str


@strawberry.type
class OrderResult:
    result: list[OrderType]


@strawberry.type
class OrderItemResult:
    result: list[OrderItemType]


class OrderService:

    @classmethod
    async def get_order(cls, db: AsyncSessionLocal, user: User) -> OrderResult | OrderError:
        items = await db.execute(select(OrderItem)
                                 .join(Order, OrderItem.order_id == Order.id)
                                 .where(Order.user_id == user.id)
                                 )

        items_list = []
        for item in items:
            items_list.append(OrderItemType.parseType(item))

        return OrderResult(result=items_list)
