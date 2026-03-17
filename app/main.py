from fastapi import FastAPI
from sqlmodel import SQLModel
from app.core.database import engine
from app.users import routes as users_router
from app.auths import routes as auths_router

app = FastAPI()

app.include_router(users_router.router)
app.include_router(auths_router.router)

@app.get("/")
def read_root():
    return {"message": "API funcionando correctamente"}

