import os

from fastapi import FastAPI


from data_domain.routers import (
    clients
)

from data_domain.init_db import init

db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")

app = FastAPI(title="Backstop Data Domain")

app.include_router(clients.router)


@app.get("/")
async def read_root():
    init()
    return {"message": "Welcome to the Data Domain"}
