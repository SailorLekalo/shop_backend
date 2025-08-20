import uuid

import strawberry
from sqlalchemy import select

from app.db.db_session import AsyncSessionLocal
from app.models.cart import CartItemType, CartItem
from app.models.product import Product
from app.models.user import User


@strawberry.type
class CartError:
    message: str


@strawberry.type
class CartResult:
    result: list[CartItemType]


@strawberry.type
class CartMessage:
    message: str


class CartService:

    @classmethod
    async def get_cart(cls, db: AsyncSessionLocal, user: User) -> CartResult | CartError:
        items = await db.execute(select(CartItem).where(CartItem.user_id == user.id))
        items = items.scalars().all()
        items_list = []
        for item in items:
            items_list.append(CartItemType.parseType(item))

        return CartResult(result=items_list)

    @classmethod
    async def add_to_cart(cls, db: AsyncSessionLocal, user: User, pid: str, qnt: int) -> CartMessage | CartError:

        check = await db.execute(select(Product).where(Product.id == pid))
        check = check.scalars().first()
        if check is None:
            return CartError(message="Продукт не существует")

        item = await db.execute(select(CartItem).where(CartItem.product_id == pid and CartItem.user_id == user.id))
        item = item.scalars().first()

        if item is None:
            if check.amount < qnt:
                return CartError(message="На складе недостаточно товара")
            new_cart_item = CartItem(user_id=user.id,
                                     product_id=pid,
                                     quantity=qnt)
            db.add(new_cart_item)
            await db.commit()
            return CartMessage(message="Товар добавлен в корзину")

        if check.amount < item.quantity + qnt:
            return CartError(message="На складе недостаточно товара")

        item.quantity += qnt
        await db.commit()
        return CartMessage(message="Товар добавлен в корзину")

    @classmethod
    async def remove_from_cart(cls, db: AsyncSessionLocal, user: User, pid: str, qnt: int) -> CartMessage | CartError:

        check_product = await db.execute(select(Product).where(Product.id == pid))
        if check_product.scalars().first() is None:
            return CartError(message="Продукт не существует")

        item = await db.execute(select(CartItem).where(CartItem.product_id == pid and CartItem.user_id == user.id))
        item = item.scalars().first()
        if item is None:
            return CartError(message="Продукта в корзине нет")
        if item.quantity > qnt:
            item.quantity -= qnt
            await db.commit()
            return CartMessage(message="Количество товаров уменьшено")
        else:
            await db.delete(item)
            await db.commit()
            return CartMessage(message="Товар удалён из корзины")
