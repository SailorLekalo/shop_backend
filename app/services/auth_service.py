import uuid
from datetime import datetime, timedelta

import strawberry
import bcrypt
from sqlalchemy import select

from app.db.db_session import AsyncSessionLocal
from app.models.sessions import Session
from app.models.user import User


@strawberry.type
class AuthSuccess:
    token: str


@strawberry.type
class AuthError:
    message: str



class AuthService:
    def __init__(self, session_expiry_minutes: int = 10):
        self.session_expiry_minutes = session_expiry_minutes
    async def register(self,
                       db: AsyncSessionLocal,
                       username: str,
                       password: str) -> AuthError | AuthSuccess:  # регистрация

        check = await db.execute(select(User).where(User.username == username))
        if check.scalars().first() is not None:
            return AuthError(message="User already exists")

        new_user = User(
            username=username,
            password_hash=bcrypt.hashpw(
                password.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')
        )

        db.add(new_user)
        await db.commit()
        return AuthSuccess(token=new_user.id)

    async def auth(self,
                   db: AsyncSessionLocal,
                   user_name: str,
                   password: str) -> AuthError | AuthSuccess:

        user = await db.execute(select(User).where(User.username == user_name))
        user = user.scalars().first()

        if user is None:
            return AuthError(message="User not found")

        if not bcrypt.checkpw(
                password.encode('utf-8'),
                user.password_hash.encode('utf-8')
        ):
            return AuthError(message="Invalid password")

        new_session = Session(
            ses_id=uuid.uuid4(),
            user_id=user.id,
            expires_at=datetime.now() + timedelta(minutes=self.session_expiry_minutes)
        )

        db.add(new_session)
        await db.commit()

        return AuthSuccess(token=f"Ваш токен сессии: {str(new_session.ses_id)}")
