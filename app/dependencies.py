from collections.abc import AsyncGenerator

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.connection import async_session

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def verify_customer_api_key(
    api_key: str | None = Security(api_key_header),
) -> str:
    if not api_key or api_key != settings.customer_api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key
