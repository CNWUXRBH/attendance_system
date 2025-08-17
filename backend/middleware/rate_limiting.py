import time
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict

# This would be better stored in a more persistent storage like Redis
rate_limit_data = defaultdict(lambda: {"count": 0, "timestamp": 0})

class RateLimitingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 100, interval: int = 60):
        super().__init__(app)
        self.limit = limit
        self.interval = interval

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()

        if client_ip not in rate_limit_data or current_time - rate_limit_data[client_ip]["timestamp"] > self.interval:
            rate_limit_data[client_ip] = {"count": 1, "timestamp": current_time}
        else:
            if rate_limit_data[client_ip]["count"] >= self.limit:
                raise HTTPException(status_code=429, detail="Too Many Requests")
            rate_limit_data[client_ip]["count"] += 1

        response = await call_next(request)
        return response