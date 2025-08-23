import httpx
import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def client():
    """HTTPX клиент, который ходит в уже запущенный uvicorn"""
    async with httpx.AsyncClient(base_url="http://app:8000") as ac:
        yield ac


@pytest.fixture(scope="session")
def state():
    """Общий стейт между тестами (куки, id-шники и т.д.)"""
    return {"cookies": {}, "order_id": None, "product_id": None}
