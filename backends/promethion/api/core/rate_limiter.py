from fastapi import Request, HTTPException, status
from datetime import datetime, timedelta

rate_limits = {}

async def rate_limiter(request: Request, max_requests: int = 10, window_seconds: int = 60):
    client_ip = request.client.host
    now = datetime.utcnow()

    if client_ip not in rate_limits:
        rate_limits[client_ip] = []

    rate_limits[client_ip] = [t for t in rate_limits[client_ip] if now - t < timedelta(seconds=window_seconds)]

    if len(rate_limits[client_ip]) >= max_requests:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests")

    rate_limits[client_ip].append(now)
