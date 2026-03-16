from fastapi import FastAPI
from sqlmodel import SQLModel
from app.core.database import engine

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "API funcionando correctamente"}

