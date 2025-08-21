from collections.abc import AsyncGenerator

import strawberry

from app.events import order_queue
from app.models.order import OrderType


@strawberry.type
class Subscription:

    @strawberry.subscription
    async def order_status_changed(self) -> AsyncGenerator[OrderType, None]:
        while True:
            order = await order_queue.get()
            yield order
