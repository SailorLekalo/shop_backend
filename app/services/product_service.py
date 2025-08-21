import strawberry
from sqlalchemy import select

from app.db.db_session import AsyncSessionLocal
from app.models.product import Product, ProductType


@strawberry.type
class ProductResult:
    result: list[ProductType]


@strawberry.type
class ProductError:
    message: str


class ProductService:
    @classmethod
    async def products(cls, db: AsyncSessionLocal) -> ProductResult:
        result = await db.execute(select(Product))
        db_products = result.scalars().all()
        to_return = [ProductType.parse_type(db_product) for db_product in db_products]

        return ProductResult(result=to_return)

    @classmethod
    async def single_product(cls, db: AsyncSessionLocal, pid: str) -> ProductResult | ProductError:
        result = await db.execute(select(Product).where(Product.id == pid))
        product = result.scalars().first()
        if product is None:
            return ProductError(message="Такого продукта не существует")
        return ProductResult(result=[ProductType.parse_type(product)])
