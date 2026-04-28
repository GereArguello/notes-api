from fastapi import Request

def key_func(request: Request):
    auth = request.headers.get("Authorization")
    forwarded = request.headers.get("X-Forwarded-For")
    ip = forwarded.split(",")[0] if forwarded else request.client.host

    if auth:
        return f"{auth}:{ip}"
    
    return ip