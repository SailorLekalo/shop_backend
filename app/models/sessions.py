import uuid
from typing import Self

import strawberry
from sqlalchemy import TIMESTAMP, UUID, Column, ForeignKey

from app.models.base import Base


class Session(Base):
    __tablename__ = "sessions"

    ses_id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"))
    expires_at = Column(TIMESTAMP)


@strawberry.type
class SessionType:
    ses_id: str
    user_id: str
    expires_at: str

    @classmethod
    def parse_type(cls, session: Session) -> Self:
        return SessionType(ses_id=str(session.ses_id),
                           user_id=str(session.user_id),
                           expires_at=str(session.expires_at))
