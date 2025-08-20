import strawberry

from strawberry.types import Info

from app.db.db_session import AsyncSessionLocal
from app.models.product import ProductType
from app.models.user import UserType, User

from app.services.auth_service import AuthService, AuthError, AuthSuccess
from app.services.cart_service import CartService, CartError, CartResult, CartMessage
from app.services.order_service import OrderError, OrderService, OrderResult
from app.services.product_service import ProductService
from app.services.session_service import SessionService, SessionError


async def auth_required(info: Info) -> UserType | SessionError:
    db = info.context["db"]
    user = await SessionService().user_by_session(info, db)
    return user


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
    async def get_order_history(self, info: Info) -> SessionError | OrderError | OrderResult:
        user = await auth_required(info)
        if isinstance(user, SessionError): return user

        orders = await OrderService.get_order(info.context["db"], user)
        return orders

    @strawberry.field
    async def get_order(self, info: Info, order_id: str) -> SessionError:
        # Этого функционала пока нет
        pass

    @strawberry.field
    async def products(self, info: Info) -> list[ProductType]:
        return await ProductService.products(info.context["db"])


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
    async def place_order(self, info: Info) -> SessionError:
        user = await auth_required(info)
        if isinstance(user, SessionError): return user
        


schema = strawberry.Schema(query=Query, mutation=Mutation)
