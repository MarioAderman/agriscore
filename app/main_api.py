import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import customer, farmer
from app.config import settings
from app.db.connection import engine
from app.models.database import Base

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(level=settings.log_level)
    logger.info("Starting AgriScore API REST")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ready")

    yield

    await engine.dispose()
    logger.info("AgriScore API REST shut down")


app = FastAPI(
    title="AgriScore API REST",
    description="Endpoints de consulta para clientes e instituciones financieras",
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

app.include_router(customer.router, prefix="/api/customer", tags=["customer"])
app.include_router(farmer.router, prefix="/api/farmer", tags=["farmer"])


@app.get("/health")
async def health():
    return {"status": "ok"}
