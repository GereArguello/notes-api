from fastapi import FastAPI
from fastapi_pagination import add_pagination
from fastapi.middleware.cors import CORSMiddleware
from app.users import routes as users_router
from app.auths import routes as auths_router
from app.subjects import routes as subjects_router
from app.topics import routes as topics_router
from app.pages import routes as pages_router
from app.tags import routes as tags_router

import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()

add_pagination(app)

app.include_router(users_router.router)
app.include_router(auths_router.router)
app.include_router(subjects_router.router)
app.include_router(topics_router.router)
app.include_router(pages_router.router)
app.include_router(tags_router.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "API funcionando correctamente"}

