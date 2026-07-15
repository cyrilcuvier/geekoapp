import asyncio
import os

import redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .sage_client import SageClient, SageUnavailable
from .simulator import initial_state, next_state
from .store import GeekoStore


def create_app(store: GeekoStore, sage_client: SageClient | None, tick_seconds: float = 3.0) -> FastAPI:
    app = FastAPI(title="geeko-api")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    async def _tick_forever():
        while True:
            state = store.get() or initial_state()
            store.set(next_state(state))
            await asyncio.sleep(tick_seconds)

    @app.on_event("startup")
    async def _start_ticking():
        if store.get() is None:
            store.set(initial_state())
        app.state.tick_task = asyncio.create_task(_tick_forever())

    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}

    @app.get("/api/geeko")
    def get_geeko():
        state = store.get() or initial_state()
        return state.model_dump()

    @app.get("/api/sage")
    def get_sage():
        if sage_client is None:
            return {"available": False}
        try:
            fortune = sage_client.fetch_fortune()
        except SageUnavailable:
            return {"available": False}
        return {"available": True, **fortune}

    return app


def _build_default_app() -> FastAPI:
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    sage_url = os.environ.get("SAGE_URL")
    tick_seconds = float(os.environ.get("TICK_SECONDS", "3"))

    store = GeekoStore(redis.Redis.from_url(redis_url))
    sage_client = SageClient(base_url=sage_url) if sage_url else None
    return create_app(store=store, sage_client=sage_client, tick_seconds=tick_seconds)


app = _build_default_app()
