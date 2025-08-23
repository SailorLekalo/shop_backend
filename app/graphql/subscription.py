from collections.abc import AsyncGenerator

import strawberry
from strawberry import Info

from app.events import broadcast
from app.models.order import OrderType
from app.services.session_service import SessionError, auth_required


@strawberry.type
class Subscription:

    @strawberry.subscription
    async def order_status_changed(self, info: Info) -> AsyncGenerator[OrderType, None]:
        user = await auth_required(info)
        if isinstance(user, SessionError):
            raise TypeError

        async with broadcast.subscribe(channel=f"orders:{user.id}") as subscriber:
            async for event in subscriber:
                data = event.message
                yield OrderType.parse_type(data, info)
