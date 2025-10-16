# backend/services/rate_limiter.py
from fastapi import Depends, Request, HTTPException, status
from fastapi_limiter.depends import RateLimiter
from fastapi_limiter import FastAPILimiter
import redis.asyncio as aioredis

async def init_rate_limiter():
    redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
    await FastAPILimiter.init(redis)

# Example dependency
rate_limit = RateLimiter(times=5, seconds=60)  # 5 requests per minute
