import uuid
from datetime import datetime, timedelta

import bcrypt
import strawberry
from sqlalchemy import delete, select

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
                       password: str,
                       handler: str | None) -> AuthError | AuthSuccess:  # регистрация

        check = await db.execute(select(User).where(User.username == username))
        if check.scalars().first() is not None:
            return AuthError(message="User already exists")

        new_user = User(
            username=username,
            password_hash=bcrypt.hashpw(
                password.encode("utf-8"),
                bcrypt.gensalt(),
            ).decode("utf-8"),
            telegram_handler=handler,
        )

        db.add(new_user)
        await db.commit()
        return AuthSuccess(message=new_user.id)

    @classmethod
    async def auth(cls,
                   db: AsyncSessionLocal,
                   user_name: str,
                   password: str,
                   cookies: list,
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

        cookies.append(
            {
                "key": "session",
                "value": str(new_session.ses_id),
                "httponly": True,
                "max_age": session_expiry_minutes * 60,
                "path": "/",
            },
        )

        return AuthSuccess(message="Вы успешно залогинены")

    @classmethod
    async def logout(cls,
                     db: AsyncSessionLocal,
                     user: User,
                     cookies: list) -> AuthSuccess:
        await db.execute(delete(Session).where(Session.user_id == user.id))
        await db.commit()
        cookies.append(
            {"key": "session", "value": "", "max_age": 0, "path": "/"},
        )
        return AuthSuccess(message="Вы разлогинились")
