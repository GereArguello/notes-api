from slowapi import Limiter

from app.core.rate_limit import key_func
from app.core.config import settings


limiter = Limiter(
    key_func=key_func,
    enabled=not settings.TESTING,
)
