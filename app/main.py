import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import webhook
from app.config import settings
from app.db.connection import engine
from app.models.database import Base

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logging.basicConfig(level=settings.log_level)
    logger.info("Starting AgriScore Core")

    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ready")

    yield

    # Shutdown
    await engine.dispose()
    logger.info("AgriScore Core shut down")


app = FastAPI(
    title="AgriScore Core",
    description="Agente IA + pipeline de evaluación agrícola",
    version="0.1.0",
    lifespan=lifespan,
)

_origins = [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
)

app.include_router(webhook.router, prefix="/api/webhook", tags=["webhook"])


@app.get("/health")
async def health():
    return {"status": "ok"}
