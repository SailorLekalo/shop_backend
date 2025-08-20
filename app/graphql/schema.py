import strawberry

from strawberry.types import Info

from app.db.db_session import AsyncSessionLocal
from app.models.product import ProductType
from app.models.user import UserType

from app.services.auth_service import AuthService, AuthError, AuthSuccess
from app.services.cart_service import CartService, CartError, CartResult, CartMessage
from app.services.order_service import OrderError, OrderService, OrderResult
from app.services.product_service import ProductService
from app.services.session_service import SessionService, SessionError


@strawberry.type
class Query:
    @strawberry.field
    async def me(self, info: Info) -> UserType | SessionError:  # По sessionid возвращает информацию о юзере
        user = await SessionService().user_by_session(info, AsyncSessionLocal())
        if isinstance(user, SessionError):
            return user

        return UserType.parseType(user)

    @strawberry.field
    async def get_cart(self, info: Info) -> SessionError | CartError | CartResult:

        user = await SessionService().user_by_session(info, AsyncSessionLocal())
        if isinstance(user, SessionError):
            return user

        cart = await CartService.get_cart(AsyncSessionLocal(), user)
        return cart

    @strawberry.field
    async def get_order_history(self, info: Info) -> SessionError | OrderError | OrderResult:

        user = await SessionService().user_by_session(info, AsyncSessionLocal())
        if isinstance(user, SessionError):
            return user

        orders = await OrderService.get_order(AsyncSessionLocal(), user)
        return orders

    @strawberry.field
    async def get_order(self, info: Info, order_id: str) -> SessionError:
        #Этого функционала пока нет
        pass

    @strawberry.field
    async def products(self) -> list[ProductType]:
        return await ProductService.products(AsyncSessionLocal())


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def register(self, username: str, password: str) -> AuthError | AuthSuccess:
        result = await AuthService().register(AsyncSessionLocal(), username, password)
        return result

    @strawberry.mutation
    async def auth(self, username: str, password: str) -> AuthError | AuthSuccess:
        result = await AuthService().auth(AsyncSessionLocal(), username, password)
        return result

    @strawberry.mutation
    async def add_to_cart(self, info: Info, product_id: str, quantity: int) -> SessionError | CartMessage | CartError:
        user = await SessionService().user_by_session(info, AsyncSessionLocal())
        if isinstance(user, SessionError):
            return user

        result = await CartService.add_to_cart(AsyncSessionLocal(), user, product_id, quantity)
        return result

    @strawberry.mutation
    async def remove_from_cart(self, info: Info, product_id: str, quantity: int) -> SessionError | CartMessage | CartError:
        user = await SessionService().user_by_session(info, AsyncSessionLocal())
        if isinstance(user, SessionError):
            return user

        result = await CartService.remove_from_cart(AsyncSessionLocal(), user, product_id, quantity)
        return result

    @strawberry.mutation
    async def place_order(self, info: Info) -> str:
        user = await SessionService().user_by_session(info, AsyncSessionLocal())
        if isinstance(user, SessionError):
            return user

schema = strawberry.Schema(query=Query, mutation=Mutation)
