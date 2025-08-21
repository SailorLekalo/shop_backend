import asyncio
import uuid
import bcrypt

from app.db.db_session import AsyncSessionLocal
from app.models.product import Product
from app.models.user import User


async def seed():
    async with AsyncSessionLocal() as session:

        products = [
            Product(id=uuid.uuid4(), name="Half-Life 2", description="Legendary FPS", price=9.99, amount=100),
            Product(id=uuid.uuid4(), name="The Witcher 3", description="RPG fantasy game", price=19.99, amount=50),
            Product(id=uuid.uuid4(), name="Cyberpunk 2077", description="Sci-fi RPG", price=29.99, amount=70),
            Product(id=uuid.uuid4(), name="Elden Ring", description="Open-world Soulslike RPG", price=39.99, amount=40),
            Product(id=uuid.uuid4(), name="Stardew Valley", description="Cozy farming sim", price=4.99, amount=200),
        ]

        session.add_all(products)

        admin_user = User(
            id=uuid.uuid4(),
            username="Yuki Nagato",
            password_hash=bcrypt.hashpw("Snowbeauty".encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            is_admin=True,
        )

        normal_user = User(
            id=uuid.uuid4(),
            username="Mikuru Asahina",
            password_hash=bcrypt.hashpw("classifieddata".encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            is_admin=False,
        )

        session.add_all([admin_user, normal_user])

        await session.commit()
        print("Тестовые данные созданы")


if __name__ == "__main__":
    asyncio.run(seed())
