import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import bank, farmer, webhook
from app.config import settings
from app.db.connection import engine
from app.models.database import Base

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logging.basicConfig(level=settings.log_level)
    logger.info("Starting AgriScore API")

    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ready")

    yield

    # Shutdown
    await engine.dispose()
    logger.info("AgriScore API shut down")


app = FastAPI(
    title="AgriScore API",
    description="Plataforma de scoring crediticio agrícola",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook.router, prefix="/api/webhook", tags=["webhook"])
app.include_router(farmer.router, prefix="/api/farmer", tags=["farmer"])
app.include_router(bank.router, prefix="/api/bank", tags=["bank"])


@app.get("/health")
async def health():
    return {"status": "ok"}
