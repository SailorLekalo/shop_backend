import strawberry
from strawberry.types import Info

from app.services.auth_service import AuthService, AuthSuccess
from app.services.cart_service import CartMessage, CartService
from app.services.notification_service import NotificationResult, NotificationService
from app.services.order_service import (
    OrderResult,
    OrderService,
    OrderStatusEnum,
)
from app.services.session_service import auth_required
from graphql import GraphQLError


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def register(self, info: Info, username: str, password: str) -> AuthSuccess:
        return await AuthService.register(info.context["db"], username, password)

    @strawberry.mutation
    async def auth(self, username: str, password: str, info: Info) -> AuthSuccess:

        return await AuthService.auth(info.context["db"], username, password, info)

    @strawberry.field
    async def logout(self, info: Info) ->  AuthSuccess:
        await auth_required(info)

        return await AuthService.logout(info.context["db"], info)

    @strawberry.mutation
    async def add_to_cart(self, product_id: str, quantity: int, info: Info) -> CartMessage:
        user = await auth_required(info)


        return await CartService.add_to_cart(info.context["db"], user, product_id, quantity)

    @strawberry.mutation
    async def remove_from_cart(self, product_id: str, quantity: int, info: Info) -> CartMessage:
        user = await auth_required(info)


        return await CartService.remove_from_cart(info.context["db"], user, product_id, quantity)

    @strawberry.mutation
    async def place_order(self, info: Info) -> OrderResult:
        user = await auth_required(info)


        return await OrderService.place_order(info.context["db"], user)

    @strawberry.mutation
    async def change_order_status(self, info: Info, order_id: str, new_status: OrderStatusEnum) -> OrderResult:

        user = await auth_required(info)

        if not user.is_admin:
            raise GraphQLError(message="Для этой операции требуется статус администратора")

        return await OrderService.change_status(info, order_id, new_status)

    @strawberry.mutation
    async def read_notifications(self,
                                 info: Info,
                                 notif_ids: list[str],
                                 ) -> NotificationResult:
        user = await auth_required(info)


        return await NotificationService.read_notifications(user, info, notif_ids)
