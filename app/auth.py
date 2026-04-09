"""Cognito JWT authentication for farmer-facing endpoints."""

import logging

import httpx
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwk, jwt

from app.config import settings

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)

_jwks_cache: dict | None = None


async def _get_jwks() -> dict:
    """Fetch and cache Cognito JWKS (JSON Web Key Set)."""
    global _jwks_cache
    if _jwks_cache is not None:
        return _jwks_cache

    if not settings.cognito_user_pool_id:
        raise HTTPException(status_code=500, detail="Cognito not configured")

    jwks_url = (
        f"https://cognito-idp.{settings.aws_default_region}.amazonaws.com/"
        f"{settings.cognito_user_pool_id}/.well-known/jwks.json"
    )

    async with httpx.AsyncClient() as client:
        resp = await client.get(jwks_url)
        resp.raise_for_status()
        _jwks_cache = resp.json()

    return _jwks_cache


def _get_signing_key(token: str, jwks: dict) -> str:
    """Find the correct signing key from JWKS for the given token."""
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")

    for key in jwks.get("keys", []):
        if key["kid"] == kid:
            return jwk.construct(key).to_pem().decode("utf-8")

    raise HTTPException(status_code=401, detail="Token signing key not found")


async def verify_cognito_token(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
) -> dict:
    """Validate Cognito JWT and return claims.

    Skips validation if Cognito is not configured (development mode).
    """
    if not settings.cognito_user_pool_id:
        return {"sub": "dev-user", "email": "dev@agriscore.local"}

    if not credentials:
        raise HTTPException(status_code=401, detail="Token de autenticación requerido")

    token = credentials.credentials
    try:
        jwks = await _get_jwks()
        signing_key = _get_signing_key(token, jwks)

        issuer = f"https://cognito-idp.{settings.aws_default_region}.amazonaws.com/{settings.cognito_user_pool_id}"

        claims = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience=settings.cognito_app_client_id,
            issuer=issuer,
        )
        return claims

    except JWTError as e:
        logger.warning("JWT validation failed: %s", e)
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
