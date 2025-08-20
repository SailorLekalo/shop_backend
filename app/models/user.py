import strawberry
from sqlalchemy import UUID, String, Boolean, Column
import uuid

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    telegram_handler = Column(String(255),default=None)


@strawberry.type
class UserType:
    id: str
    username: str
    isAdmin: bool
    telegram_handler: str

    @classmethod
    def parseType(cls, user: User):
        return UserType(
            id=str(user.id),
            username=user.username,
            isAdmin=user.is_admin,
            telegram_handler=user.telegram_handler
        )
