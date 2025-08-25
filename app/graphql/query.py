import strawberry
from strawberry.types import Info

from app.models.user import UserType
from app.services.cart_service import CartResult, CartService
from app.services.notification_service import (
    NotificationReadResult,
    NotificationService,
)
from app.services.order_service import (
    OrderResult,
    OrderService,
)
from app.services.product_service import ProductResult, ProductService
from app.services.session_service import auth_required


@strawberry.type
class Query:
    @strawberry.field
    async def me(self, info: Info) -> UserType:

        user = await auth_required(info)



        return UserType.parse_type(user)

    @strawberry.field
    async def get_cart(self, info: Info) -> CartResult:
        user = await auth_required(info)


        return await CartService.get_cart(info.context["db"], user)

    @strawberry.field
    async def get_orders(self, info: Info) -> OrderResult:

        user = await auth_required(info)


        return await OrderService.get_orders(info.context["db"], user, info)

    @strawberry.field
    async def get_single_order(self, info: Info, order_id: str) -> OrderResult:
        user = await auth_required(info)


        return await OrderService.get_single_order(info.context["db"], user, order_id, info)

    @strawberry.field
    async def products(self, info: Info) -> ProductResult:
        return await ProductService.products(info.context["db"])

    @strawberry.field
    async def get_product(self, info: Info, pid: str) -> ProductResult:
        return await ProductService.single_product(info.context["db"], pid)

    @strawberry.field
    async def get_notifications(self, info: Info) -> NotificationReadResult:
        user = await auth_required(info)



        return await NotificationService.get_notififcations(user, info.context["db"])
