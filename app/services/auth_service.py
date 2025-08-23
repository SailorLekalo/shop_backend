import uuid
from datetime import datetime, timedelta

import bcrypt
import strawberry
from sqlalchemy import delete, select
from strawberry import Info

from app.db.db_session import AsyncSessionLocal
from app.models.sessions import Session
from app.models.user import User


@strawberry.type
class AuthSuccess:
    message: str


@strawberry.type
class AuthError:
    message: str


class AuthService:

    @classmethod
    async def register(cls,
                       db: AsyncSessionLocal,
                       username: str,
                       password: str) -> AuthError | AuthSuccess:  # регистрация

        check = await db.execute(select(User).where(User.username == username))
        if check.scalars().first() is not None:
            return AuthError(message="User already exists")

        new_user = User(
            username=username,
            password_hash=bcrypt.hashpw(
                password.encode("utf-8"),
                bcrypt.gensalt(),
            ).decode("utf-8"),
        )

        db.add(new_user)
        await db.commit()
        return AuthSuccess(message=new_user.id)

    @classmethod
    async def auth(cls,
                   db: AsyncSessionLocal,
                   user_name: str,
                   password: str,
                   info: Info,
                   session_expiry_minutes: int = 10) -> AuthError | AuthSuccess:

        user = await db.execute(select(User).where(User.username == user_name))
        user = user.scalars().first()

        if user is None:
            return AuthError(message="User not found")

        if not bcrypt.checkpw(
                password.encode("utf-8"),
                user.password_hash.encode("utf-8"),
        ):
            return AuthError(message="Invalid password")

        new_session = Session(
            ses_id=uuid.uuid4(),
            user_id=user.id,
            expires_at=datetime.now() + timedelta(minutes=session_expiry_minutes),
        )

        db.add(new_session)
        await db.commit()

        info.context["response"].set_cookie(
            key="session",
            value=new_session.ses_id,
            httponly=True,
            samesite="lax",
            max_age=session_expiry_minutes * 60,
            path="/",
        )

        return AuthSuccess(message="Вы успешно залогинены")

    @classmethod
    async def logout(cls,
                     db: AsyncSessionLocal,
                     info: Info) -> AuthSuccess:
        request = info.context["request"]
        sessionid = request.cookies.get("session")
        await db.execute(delete(Session).where(Session.ses_id == sessionid))
        await db.commit()

        info.context["response"].set_cookie(
            key="session",
            value="",
            max_age=0,
            path="/",
        )

        return AuthSuccess(message="Вы разлогинились")
