from slowapi import Limiter

from app.core.rate_limit import key_func


limiter = Limiter(key_func=key_func)
