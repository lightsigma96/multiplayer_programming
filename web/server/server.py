"""Let AI add proper expection handling, where dependencies return None for error and server propogates important error to client, for now any error can stop server"""

from sqlite3 import DatabaseError
from uuid import uuid4
from fastapi import FastAPI, Response, Request
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis
from pydantic import BaseModel
import uvicorn
from auth import session_handler as sh
import string
import secrets
import logging
import server_types
import os
from db import db_handler

## constants
credential_db_path: str = os.path.join(os.getcwd(), "db/credentials.db")

## Init
app = FastAPI()

allowed_origin = ["http://localhost:5200"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger: logging.Logger = logging.getLogger(__name__)

session_redis: Redis = Redis(host="localhost", port=6900, decode_responses=True)
credential_db: db_handler.DB_Handler = db_handler.DB_Handler(credential_db_path)

credential_db_schema: server_types.Schema = server_types.Schema(
    table_name="logged_user", columns=[("username", "TEXT"), ("password", "TEXT")]
)

credential_db.create_table(credential_db_schema)

async def refresh_or_create_session(req: Request, res: Response):
    existing_session_id: str | None = req.cookies.get("session_id")

    if not existing_session_id:

        guest_username: str = "".join(
            secrets.choice(string.ascii_letters + string.digits) for _ in range(29)
        )

        new_sesh: server_types.Session = server_types.Session(
            user=guest_username, is_logged_in=0
        )
        session_id: str | None = await sh.add_session(
            session_redis, logger, new_sesh, 60
        )

        if not session_id:
            logging.info(f" COULD NOT ADD SESSION WITH")
            return {"server_msg": "session could not be added"}

        res.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=60,
        )
        logging.info(f" ADDED SESSION WITH SESSION ID {session_id} ")
        return {"server_msg": "session added"}

    else:
        remaining_time: int | None = await sh.get_remaining_time(
            redis_instance=session_redis, logger=logger, session_id=existing_session_id
        )

        if remaining_time and remaining_time < 15:
            await session_redis.expire(f"session:{existing_session_id}", 60, xx=True)
            res.set_cookie(
                key="session_id",
                value=existing_session_id,
                httponly=True,
                secure=False,
                samesite="lax",
                max_age= remaining_time + 60, ## use variable dont hardcode
            )
        else:
            return {"server_msg": "session already exists"}

## Endpoints
@app.get("/home")
async def home(req : Request, res : Response):
    await refresh_or_create_session(req,res) 
    return {"server_meassge":"home"}

@app.get("/about")
async def about(req : Request, res : Response):
    await refresh_or_create_session(req,res) 
    return {"server_meassge":"about"}

@app.post("/sign_up")
async def sign_up(
    req: Request, res: Response, sign_up_credentials: server_types.SignupCredentials
):
    # Later replace sqlite

    session_id: str | None = req.cookies.get("session_id")

    if not session_id:
        raise HTTPException(
            status_code=400, detail="Session-ID not found for guest user bad request"
        )

    db_res: str | None = credential_db.insert_table(
        "logged_user", (sign_up_credentials.username, sign_up_credentials.password)
    )
    if db_res:
        logging.info(db_res)
    else:
        raise DatabaseError("Error inserting value in db")

    # TODO Handle refersh expiry for logged in user
    temp_session: server_types.Session | None = await sh.get_session(
        session_redis, logger, session_id
    )

    if not temp_session:
        return {"server_msg": "user not signed up successfully"}

    new_session: server_types.Session = server_types.Session(
        user=sign_up_credentials.username, is_logged_in=1
    )
    await sh.delete_session(session_redis, logger, session_id)

    new_session_id: str | None = await sh.add_session(
        session_redis, logger, new_session, 60
    )

    if new_session_id:
        res.set_cookie(
            key="session_id",
            value=new_session_id,
            httponly=True,
            secure=False,  # enable this later
            samesite="lax",
            max_age=60,
        )
    logging.info(f" ADDED SESSION WITH SESSION ID {session_id} ")

    return {"server_msg": "user signed up successfully"}


if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
