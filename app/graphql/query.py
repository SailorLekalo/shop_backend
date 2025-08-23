import strawberry
from strawberry.types import Info

from app.models.user import UserType
from app.services.cart_service import CartError, CartResult, CartService
from app.services.notification_service import (
    NotificationReadResult,
    NotificationService,
)
from app.services.order_service import (
    OrderError,
    OrderResult,
    OrderService,
)
from app.services.product_service import ProductError, ProductResult, ProductService
from app.services.session_service import SessionError, auth_required


@strawberry.type
class Query:
    @strawberry.field
    async def me(self, info: Info) -> UserType | SessionError:

        user = await auth_required(info)

        if isinstance(user, SessionError):
            return user

        return UserType.parse_type(user)

    @strawberry.field
    async def get_cart(self, info: Info) -> SessionError | CartError | CartResult:
        user = await auth_required(info)
        if isinstance(user, SessionError):
            return user

        return await CartService.get_cart(info.context["db"], user)

    @strawberry.field
    async def get_orders(self, info: Info) -> SessionError | OrderResult | OrderError:

        user = await auth_required(info)
        if isinstance(user, SessionError):
            return user

        return await OrderService.get_orders(info.context["db"], user, info)

    @strawberry.field
    async def get_single_order(self, info: Info, order_id: str) -> SessionError | OrderResult | OrderError:
        user = await auth_required(info)
        if isinstance(user, SessionError):
            return user

        return await OrderService.get_single_order(info.context["db"], user, order_id, info)

    @strawberry.field
    async def products(self, info: Info) -> ProductResult:
        return await ProductService.products(info.context["db"])

    @strawberry.field
    async def get_product(self, info: Info, pid: str) -> ProductResult | ProductError:
        return await ProductService.single_product(info.context["db"], pid)

    @strawberry.field
    async def get_notifications(self, info: Info) -> SessionError | NotificationReadResult:
        user = await auth_required(info)

        if isinstance(user, SessionError):
            return user

        return await NotificationService.get_notififcations(user, info.context["db"])
