from fastapi import  FastAPI,Response 
from fastapi.middleware.cors import CORSMiddleware
from typing import Awaitable
from redis.asyncio import Redis
from pydantic import BaseModel
import uvicorn
from auth import session_handler as sh
import string
import secrets
import logging


## types
class Cookie(BaseModel):
    session_id : str


app = FastAPI()

allowed_origin = [
        "http://localhost:5200"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origin,
    allow_credentials=True,
    allow_methods = ["*"],
    allow_headers=["*"],
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

session_redis : Redis = Redis(host="localhost",port=6900,decode_responses=True)


@app.post("/")
async def init(res : Response):
    guest_username : str =  "".join(secrets.choice(string.ascii_letters+ string.digits) for _ in range(29))

    session_id : str = await sh.add_user(session_redis,guest_username)
    logging.info(f" ADDED SESSION WITH SESSION ID {session_id} ")
   
    res.set_cookie(
    key="Session-ID",
    value=session_id,
    httponly=True,
    secure=True,
    samesite="lax"
    )

    return {"server_msg": "session added"}

if __name__ == "__main__":
    uvicorn.run("server:app",host = "127.0.0.1", port=8000,reload=True) 
