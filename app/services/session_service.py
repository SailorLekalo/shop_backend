from datetime import datetime

import strawberry
from sqlalchemy import select
from strawberry import Info

from app.db.db_session import AsyncSessionLocal
from app.models.sessions import Session
from app.models.user import User


@strawberry.type
class SessionError:
    message: str


class SessionService:
    async def check_session_expiration(self, db: AsyncSessionLocal, check_ses: Session):
        async with db as session:
            check = await session.execute(select(Session).where(Session.ses_id == check_ses.ses_id))
            check = check.scalars().first()
            if check.expires_at > datetime.now():
                return False
            return True

    async def user_by_session(self, info: Info, db: AsyncSessionLocal) -> User | SessionError:
        async with db as session:
            request = info.context["request"]
            auth_header = request.headers.get("authorization")

            sessionid = None
            if auth_header and auth_header.startswith("Bearer "):
                sessionid = auth_header[len("Bearer "):]

            check = await session.execute(select(Session).where(Session.ses_id == sessionid))
            check = check.scalars().first()

            if check is None:
                return SessionError(message="Сессия не существует")

            if await self.check_session_expiration(db, check):
                return SessionError(message="Сессия истекла")

            user = await session.execute(select(User).where(User.id == check.user_id))
            return user.scalars().first()
