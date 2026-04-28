from fastapi import FastAPI
from fastapi_pagination import add_pagination
from fastapi.middleware.cors import CORSMiddleware

from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse  
from slowapi.middleware import SlowAPIMiddleware

from app.users import routes as users_router
from app.auths import routes as auths_router
from app.subjects import routes as subjects_router
from app.topics import routes as topics_router
from app.pages import routes as pages_router
from app.tags import routes as tags_router

from app.core.limiter import limiter

import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda request, exc: JSONResponse(
    status_code=429,
    content={"detail": "Too many requests"}
))


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "https://notes-api-ten-beige.vercel.app",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(SlowAPIMiddleware)

add_pagination(app)

app.include_router(users_router.router)
app.include_router(auths_router.router)
app.include_router(subjects_router.router)
app.include_router(topics_router.router)
app.include_router(pages_router.router)
app.include_router(tags_router.router)

@app.get("/")
def read_root():
    return {"message": "API funcionando correctamente"}

