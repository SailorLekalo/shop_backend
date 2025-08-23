import uuid

import strawberry
from sqlalchemy import select, update
from strawberry import Info

from app.db.db_session import AsyncSessionLocal
from app.events import broadcast
from app.models.notifications import NotificationEnum, Notifications, NotificationsType
from app.models.order import Order
from app.models.user import User


@strawberry.type
class NotificationResult:
    message: str

@strawberry.type()
class NotificationReadResult:
    result: list[NotificationsType]


class NotificationService:

    @classmethod
    async def notificate_websocket(cls,
                                   order: Order,
                                   db: AsyncSessionLocal) -> None:

        notif = Notifications(
            id=uuid.uuid4(),
            user_id=order.user_id,
            order_id=order.id,
            status=NotificationEnum.UNREAD,
        )
        db.add(notif)
        await db.commit()
        await broadcast.publish(
            channel=f"orders:{order.user_id}",
            message=order,
        )

    @classmethod
    async def get_notififcations(cls, user: User, db: AsyncSessionLocal) -> NotificationReadResult:
        result = await db.execute(
            select(Notifications).where(Notifications.user_id == user.id),
        )
        notifications = result.scalars().all()
        return NotificationReadResult(result=[NotificationsType.parse_type(n) for n in notifications])

    @classmethod
    async def read_notifications(cls, user: User, info: Info, notif_ids: list[str]) -> NotificationResult:
        db = info.context["db"]

        q = (
            update(Notifications)
            .where(
                Notifications.user_id == user.id,
                Notifications.id.in_(notif_ids),
            )
            .values(status=NotificationEnum.READ)
            .execution_options(synchronize_session="fetch")
        )

        await db.execute(q)
        await db.commit()
        return NotificationResult(message="Notifications read")
