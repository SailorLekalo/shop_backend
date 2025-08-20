from sqlalchemy import select

from app.db.db_session import AsyncSessionLocal
from app.models.product import ProductType, Product


class ProductService:
    @classmethod
    async def products(cls, db: AsyncSessionLocal) -> list[ProductType]:
        result = await db.execute(select(Product))
        db_products = result.scalars().all()
        to_return = []
        for db_product in db_products:
            to_return.append(ProductType.parseType(db_product))
        return to_return