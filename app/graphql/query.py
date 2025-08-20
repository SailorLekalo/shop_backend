import strawberry

from strawberry.types import Info

from app.models.product import ProductType
from app.models.user import UserType

from app.services.cart_service import CartService, CartError, CartResult
from app.services.order_service import OrderError, OrderService, OrderResult, OrderItemResult
from app.services.product_service import ProductService
from app.services.session_service import SessionError, auth_required


@strawberry.type
class Query:
    @strawberry.field
    async def me(self, info: Info) -> UserType | SessionError:  # По sessionid возвращает информацию о юзере
        user = await auth_required(info)
        if isinstance(user, SessionError): return user

        return UserType.parseType(user)

    @strawberry.field
    async def get_cart(self, info: Info) -> SessionError | CartError | CartResult:
        user = await auth_required(info)
        if isinstance(user, SessionError): return user

        cart = await CartService.get_cart(info.context["db"], user)
        return cart

    @strawberry.field
    async def get_orders(self, info: Info) -> SessionError | OrderResult | OrderError:
        user = await auth_required(info)
        if isinstance(user, SessionError): return user

        return await OrderService.get_orders(info.context["db"], user)

    @strawberry.field
    async def get_order_items(self, info: Info, order_id: str) -> SessionError | OrderItemResult | OrderError:
        user = await auth_required(info)
        if isinstance(user, SessionError): return user

        return await OrderService.get_order_items(info.context["db"], user, order_id)

    @strawberry.field
    async def products(self, info: Info) -> list[ProductType]:
        return await ProductService.products(info.context["db"])
