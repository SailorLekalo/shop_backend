
import strawberry
from sqlalchemy import select

from app.db.db_session import AsyncSessionLocal
from app.models.cart import CartItem, CartItemType
from app.models.product import Product
from app.models.user import User
from graphql import GraphQLError


@strawberry.type
class CartResult:
    result: list[CartItemType]


@strawberry.type
class CartMessage:
    message: str


class CartService:

    @classmethod
    async def get_cart(cls, db: AsyncSessionLocal, user: User) -> CartResult :
        result = await db.execute(
            select(CartItem, Product)
            .join(Product, Product.id == CartItem.product_id)
            .where(CartItem.user_id == user.id),
        )
        rows = result.all()

        items_list = [
            CartItemType.parse_type(cart_item, product)
            for cart_item, product in rows
        ]

        return CartResult(result=items_list)

    @classmethod
    async def add_to_cart(cls, db: AsyncSessionLocal, user: User, pid: str, qnt: int) -> CartMessage :

        check = await db.execute(select(Product).where(Product.id == pid))
        check = check.scalars().first()
        if check is None:
            raise GraphQLError(message="Продукт не существует")

        item = await db.execute(select(CartItem).where(CartItem.product_id == pid, CartItem.user_id == user.id))
        item = item.scalars().first()

        if item is None:
            if check.amount < qnt:
                raise GraphQLError(message="На складе недостаточно товара")
            new_cart_item = CartItem(user_id=user.id,
                                     product_id=pid,
                                     quantity=qnt,
                                     price=check.price*qnt)
            db.add(new_cart_item)
            await db.commit()
            return CartMessage(message="Товар добавлен в корзину")

        if check.amount < item.quantity + qnt:
            raise GraphQLError(message="На складе недостаточно товара")

        item.quantity += qnt
        await db.commit()
        return CartMessage(message="Товар добавлен в корзину")

    @classmethod
    async def remove_from_cart(cls, db: AsyncSessionLocal, user: User, pid: str, qnt: int) -> CartMessage:

        check_product = await db.execute(select(Product).where(Product.id == pid))
        if check_product.scalars().first() is None:
            raise GraphQLError(message="Продукт не существует")

        item = await db.execute(select(CartItem).where(CartItem.product_id == pid, CartItem.user_id == user.id))
        item = item.scalars().first()
        if item is None:
            raise GraphQLError(message="Продукта в корзине нет")
        if item.quantity > qnt:
            item.quantity -= qnt
            await db.commit()
            return CartMessage(message="Количество товаров уменьшено")
        await db.delete(item)
        await db.commit()
        return CartMessage(message="Товар удалён из корзины")
