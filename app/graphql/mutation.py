import strawberry
from strawberry.types import Info

from app.services.auth_service import AuthError, AuthService, AuthSuccess
from app.services.cart_service import CartError, CartMessage, CartService
from app.services.order_service import (
    OrderError,
    OrderResult,
    OrderService,
    OrderStatusEnum,
)
from app.services.session_service import SessionError, auth_required


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def register(self, info: Info, username: str, password: str, handler: str | None = None) -> AuthError | AuthSuccess:
        return await AuthService.register(info.context["db"], username, password, handler)


    @strawberry.mutation
    async def auth(self, username: str, password: str, info: Info) -> AuthError | AuthSuccess:

        return await AuthService.auth(info.context["db"], username, password, info.context["cookies"])


    @strawberry.field
    async def logout(self, info: Info) -> SessionError | AuthSuccess:
        user = await auth_required(info)
        if isinstance(user, SessionError):
            return user

        return await AuthService.logout(info.context["db"], user, info.context["cookies"])

    @strawberry.mutation
    async def add_to_cart(self, product_id: str, quantity: int, info: Info) -> SessionError | CartMessage | CartError:
        user = await auth_required(info)
        if isinstance(user, SessionError):
            return user

        return await CartService.add_to_cart(info.context["db"], user, product_id, quantity)

    @strawberry.mutation
    async def remove_from_cart(self, product_id: str, quantity: int, info: Info) -> SessionError | CartMessage | CartError:
        user = await auth_required(info)
        if isinstance(user, SessionError):
            return user

        return await CartService.remove_from_cart(info.context["db"], user, product_id, quantity)

    @strawberry.mutation
    async def place_order(self, info: Info) -> SessionError | OrderResult | OrderError:
        user = await auth_required(info)
        if isinstance(user, SessionError):
            return user

        return await OrderService.place_order(info.context["db"], user)

    @strawberry.mutation
    async def change_order_status(self, info: Info, order_id: str, new_status: OrderStatusEnum) -> SessionError | OrderResult | OrderError:
        user = await auth_required(info)
        if isinstance(user, SessionError):
            return user
        if not user.is_admin:
            return SessionError(message="Для этой операции требуется статус администратора")

        return await OrderService.change_status(info, order_id, new_status)
