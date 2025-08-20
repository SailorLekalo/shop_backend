import os
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from strawberry.fastapi import GraphQLRouter

from app.db.db_session import AsyncSessionLocal
from app.graphql.schema import schema

load_dotenv(f"{Path(__file__).parent}/settings/.env")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")


bot = Bot(token=TELEGRAM_TOKEN,
          default=DefaultBotProperties(parse_mode=ParseMode.HTML)
          )
dp = Dispatcher()

app = FastAPI()

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    async with AsyncSessionLocal() as session:
        request.state.db = session
        try:
            response = await call_next(request)
        finally:
            await session.close()
    return response
async def get_context(request: Request):
    return {
        "db": request.state.db,
        "request": request,
        "bot": bot
    }


graphql_app = GraphQLRouter(schema, context_getter=get_context)
app.include_router(graphql_app, prefix="/graphql")