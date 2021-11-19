import os

# import json
# from typing import Dict, Any, List, Optional
from fastapi import APIRouter

from rethinkdb import RethinkDB


def rethinkdb_wrap():
    return RethinkDB()


db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
router = APIRouter(tags=["clients"])


@router.get("/clients")
async def read_chiefs():
    with rethinkdb_wrap().connect(host=db_host, port=db_port) as conn:
        res = RethinkDB().db("Risky").table("clients").run(conn)
        clients = list(res)
    return clients
