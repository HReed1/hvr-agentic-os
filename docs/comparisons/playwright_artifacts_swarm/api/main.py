from contextlib import asynccontextmanager
from fastapi import FastAPI
import time

from api.routers import items, ui
from api.database import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(items.router)
app.include_router(ui.router)

@app.get("/api/v1/ping")
async def ping():
    return {"status": "pong", "timestamp": time.time()}


@app.get('/live')
async def liveness_probe():
    return {"status": "live"}
