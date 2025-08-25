from datetime import datetime

from sqlalchemy import select
from strawberry import Info

from app.db.db_session import AsyncSessionLocal
from app.models.sessions import Session
from app.models.user import User
from graphql import GraphQLError


async def auth_required(info: Info) -> User:
    db = info.context["db"]
    return await SessionService().user_by_session(info, db)


class SessionService:
    async def check_session_expiration(self, check_ses: Session) -> True | False:
        return not (check_ses.expires_at > datetime.now())

    async def user_by_session(self, info: Info, db: AsyncSessionLocal) -> User:

        request = info.context["request"]
        sessionid = request.cookies.get("session")


        check = await db.execute(select(Session).where(Session.ses_id == sessionid))
        check = check.scalars().first()
        if check is None:
            raise GraphQLError(message="Сессия не существует")

        if await self.check_session_expiration(check):
            raise GraphQLError(message="Сессия истекла")

        user = await db.execute(select(User).where(User.id == check.user_id))

        return user.scalars().first()
