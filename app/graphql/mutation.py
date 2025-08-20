import strawberry

from strawberry.types import Info

from app.services.auth_service import AuthService, AuthError, AuthSuccess
from app.services.cart_service import CartService, CartError, CartMessage
from app.services.order_service import OrderError, OrderService, OrderResult

from app.services.session_service import SessionError, auth_required


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def register(self, username: str, password: str, info: Info) -> AuthError | AuthSuccess:
        result = await AuthService().register(info.context["db"], username, password)
        return result

    @strawberry.mutation
    async def auth(self, username: str, password: str, info: Info) -> AuthError | AuthSuccess:
        result = await AuthService().auth(info.context["db"], username, password)
        return result

    @strawberry.mutation
    async def add_to_cart(self, product_id: str, quantity: int, info: Info) -> SessionError | CartMessage | CartError:
        user = await auth_required(info)
        if isinstance(user, SessionError): return user

        result = await CartService.add_to_cart(info.context["db"], user, product_id, quantity)
        return result

    @strawberry.mutation
    async def remove_from_cart(self, product_id: str, quantity: int, info: Info) -> SessionError | CartMessage | CartError:
        user = await auth_required(info)
        if isinstance(user, SessionError): return user

        result = await CartService.remove_from_cart(info.context["db"], user, product_id, quantity)
        return result

    @strawberry.mutation
    async def place_order(self, info: Info) -> SessionError | OrderResult | OrderError:
        user = await auth_required(info)
        if isinstance(user, SessionError): return user

        return await OrderService.place_order(info.context["db"], user)
