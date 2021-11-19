import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from dateutil.relativedelta import relativedelta
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Backstop Edge Service")

origins = [
    "*",
    "http://localhost",
    "https://localhost",
    "http://localhost/*",
    "https://localhost/*",
    "https://whiteasteroid01.icl.gtri.org",
    "https://whiteasteroid01.icl.gtri.org/*",
    "https://whiteasteroid02.icl.gtri.org",
    "https://whiteasteroid02.icl.gtri.org/*",
    "http://localhost:80",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

dd_host = os.getenv("DD_HOST")
dd_port = os.getenv("DD_PORT")
dd_uri = os.getenv("DD_URI")

cal_host = os.getenv("cal_HOST")
cal_port = os.getenv("cal_PORT")

dd_url = "http://" + dd_host + ":" + dd_port
cal_url = "http://" + cal_host + ":" + cal_port


@app.get("/edge/")
async def read_root():
    return {"message": "Welcome to Risky Edge Service"}



