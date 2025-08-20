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


async def auth_required(info: Info) -> User | SessionError:
    db = info.context["db"]
    user = await SessionService().user_by_session(info, db)
    return user


class SessionService:
    async def check_session_expiration(self, check_ses: Session):
        if check_ses.expires_at > datetime.now():
            return False
        return True

    async def user_by_session(self, info: Info, db: AsyncSessionLocal) -> User | SessionError:

        request = info.context["request"]
        auth_header = request.headers.get("authorization")
        sessionid = None

        if auth_header and auth_header.startswith("Bearer "):
            sessionid = auth_header[len("Bearer "):]
        check = await db.execute(select(Session).where(Session.ses_id == sessionid))
        check = check.scalars().first()

        if check is None:
            return SessionError(message="Сессия не существует")

        if await self.check_session_expiration(check):
            return SessionError(message="Сессия истекла")
        user = await db.execute(select(User).where(User.id == check.user_id))

        return user.scalars().first()


