from fastapi import FastAPI
from fastapi_pagination import add_pagination
from app.users import routes as users_router
from app.auths import routes as auths_router
from app.subjects import routes as subjects_router

app = FastAPI()

add_pagination(app)

app.include_router(users_router.router)
app.include_router(auths_router.router)
app.include_router(subjects_router.router)

@app.get("/")
def read_root():
    return {"message": "API funcionando correctamente"}

