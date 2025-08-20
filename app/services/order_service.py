
import uuid

import strawberry
from aiogram import Bot
from sqlalchemy import select
from strawberry import Info

from app.db.db_session import AsyncSessionLocal
from app.models.cart import CartItem
from app.models.order import OrderItemType, OrderItem, OrderType, Order
from app.models.user import User

import aiogram

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
    async def get_orders(cls, db: AsyncSessionLocal, user: User) -> OrderResult:
        result = await db.execute(select(Order).where(Order.user_id == user.id))
        orders = result.scalars().all()

        return OrderResult(result=[OrderType.parseType(o) for o in orders])

    @classmethod
    async def get_order_items(cls,
                              db: AsyncSessionLocal,
                              user: User,
                              order_id: str) -> OrderItemResult | OrderError:

        order_check = await db.execute(
            select(Order)
            .where(Order.id == order_id,
                  Order.user_id == user.id)
        )
        order = order_check.scalars().first()
        if not order:
            return OrderError(message="Заказ не найден или доступ запрещён")

        result = await db.execute(select(OrderItem).where(OrderItem.order_id == order_id))
        items = result.scalars().all()

        items_list = [OrderItemType.parseType(item) for item in items]
        return OrderItemResult(result=items_list)

    @classmethod
    async def place_order(cls, db: AsyncSessionLocal, user: User) -> OrderResult | OrderError:
        items = await db.execute(select(CartItem).where(CartItem.user_id == user.id))
        items = items.scalars().all()

        if not items:
            return OrderError(message="Корзина пуста")

        order = Order(user_id=user.id,
                      id=uuid.uuid4(),
                      status="In process",
                      price=0)

        for item in items:
            order_item = OrderItem(order_id=order.id,
                                   product_id=item.product_id,
                                   quantity=item.quantity,
                                   price=item.price)
            db.add(order_item)
            order.price += item.price

        db.add(order)

        for item in items:
            await db.delete(item)

        await db.commit()
        return OrderResult(result=[order])

    @classmethod
    async def change_status(cls, info: Info, order_id: str, new_status: str):
        db = info.context["db"]
        result = await db.execute(
            select(Order).where(Order.id == uuid.UUID(order_id))
        )
        order = result.scalars().first()

        if order is None:
            return OrderError(message="Такого заказа не существует")

        order.status = new_status
        await db.commit()
        await db.refresh(order)

        user_result = await db.execute(select(User).where(User.id == order.user_id))
        user = user_result.scalars().first()

        if user and user.telegram_handler:
            await cls._notificate(order.id,
                                  order.user_id,
                                  new_status,
                                  info.context["bot"],
                                  user.telegram_handler
                                  )

        return OrderResult(result=[OrderType.parseType(order)])

    @classmethod
    async def _notificate(cls,
                          order_id: str,
                          user_id: str,
                          new_status: str,
                          bot: Bot,
                          handler: str):
        message = (
            f"📦 Новый статус заказа\n\n"
            f"🆔 Order ID: <code>{order_id}</code>\n"
            f"👤 User ID: <code>{user_id}</code>\n"
            f"📌 Status: <b>{new_status}</b>"
        )
        await bot.send_message(handler, message)
