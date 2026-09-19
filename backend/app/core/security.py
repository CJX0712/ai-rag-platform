"""Optional shared API-key guard.

When ``API_KEY`` is configured, every protected endpoint requires
``Authorization: Bearer <API_KEY>``. When unset, the API is open (dev/demo).
Production deployments should front this with a real identity provider.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings

settings = get_settings()
_bearer = HTTPBearer(auto_error=False)


def require_api_key(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> None:
    if not settings.API_KEY:
        return  # auth disabled
    if creds is None or creds.credentials != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
