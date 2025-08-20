import strawberry
from sqlalchemy import UUID, TIMESTAMP, Column, ForeignKey
import uuid

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
    def parseType(cls, session: Session):
        return SessionType(ses_id=str(session.ses_id),
                           user_id=str(session.user_id),
                           expires_at=str(session.expires_at))
