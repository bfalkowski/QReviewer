"""Security middleware for QReviewer API."""

import os
from typing import Union
from fastapi import Header, HTTPException, status


async def require_api_key(authorization: Union[str, None] = Header(default=None)) -> bool:
    """
    Validate API key from Authorization header.
    
    If QREVIEWER_API_KEY is not set, allows all requests (dev mode).
    If set, requires valid Bearer token.
    """
    api_key = os.getenv("QREVIEWER_API_KEY")
    
    # Dev mode: no API key required
    if not api_key:
        return True
    
    # Production mode: require valid Bearer token
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization format. Use 'Bearer <token>'"
        )
    
    token = authorization.split(" ", 1)[1]
    if token != api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    
    return True
