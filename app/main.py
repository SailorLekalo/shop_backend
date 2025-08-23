from collections.abc import Callable
from typing import Awaitable

from fastapi import FastAPI, Request, Response
from starlette.websockets import WebSocket
from strawberry.fastapi import GraphQLRouter

from app.db.db_session import AsyncSessionLocal
from app.events import broadcast
from app.graphql.schema import schema

app = FastAPI()



@app.middleware("http")
async def db_session_middleware(request: Request,
                                call_next: Callable[[Request],
                                Awaitable[Response]],
                                ) -> Response:
    async with AsyncSessionLocal() as session:
        request.state.db = session

        return await call_next(request)


async def get_context(request: Request = None, websocket: WebSocket = None) -> dict:
    if request is not None:

        if not hasattr(request.state, "cookies"):
            request.state.cookies = []
        return {
            "db": request.state.db,
            "request": request,
            "cookies": request.state.cookies,
        }
    if websocket is not None:
        async with AsyncSessionLocal() as session:
            return {
                "db": session,
                "request": websocket,
            }
    return {}


graphql_app = GraphQLRouter(schema, context_getter=get_context)
app.include_router(graphql_app, prefix="/graphql")


@app.on_event("startup")
async def startup() -> None:
    await broadcast.connect()

@app.on_event("shutdown")
async def shutdown() -> None:
    await broadcast.disconnect()
