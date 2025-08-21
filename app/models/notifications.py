import uuid

import strawberry
from sqlalchemy import UUID, Column, ForeignKey, String
from typing_extensions import Self

from app.models.base import Base


class Notifications(Base):
    __tablename__ = "notifications"

    id = Column(UUID, primary_key=True, default=uuid.uuid4())
    user_id = Column(ForeignKey("users.id"))
    order_id = Column(ForeignKey("orders.id"))
    channel = Column(String(50))


@strawberry.type
class NotificationsType:
    id: str
    user_id: str
    order_id: str
    channel: str

    @classmethod
    def parse_type(cls, notifications: Notifications) -> Self:
        return NotificationsType(id=str(notifications.id),
                                 user_id=str(notifications.user_id),
                                 order_id=str(notifications.order_id),
                                 channel=str(notifications.channel))
