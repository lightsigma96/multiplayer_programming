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

class SignupCredentials(BaseModel):
    username: str
    password: str
    session_id: str


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
    table_name="logged_in", columns=[("username", "STRING"), ("password", "STRING")]
)

credential_db.create_table(credential_db_schema)


## Endpoints
@app.post("/")
async def create_guest_session(res: Response):
    guest_username: str = "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(29)
    )

    new_sesh : server_types.Session = server_types.Session(user=guest_username, is_logged_in=str( False ))
    session_id: str | None = await sh.add_user(
        session_redis, logger, new_sesh 
    )

    if not session_id:
        logging.info(f" COULD NOT ADD SESSION WITH")
        return {"server_msg": "session could not be added"}

    res.set_cookie(
        key="Session-ID",
        value=session_id,
        httponly=True,
        secure=False,
        samesite="lax",
        expires=60,
    )
    logging.info(f" ADDED SESSION WITH SESSION ID {session_id} ")
    return {"server_msg": "session added"}

    

@app.post("/sign_up")
async def sign_up(req: Request, res : Response, sign_up_credentials: SignupCredentials):
    # Later replace sqlite

    session_id: str | None = req.cookies.get("Session-ID")

    if not session_id:
        raise HTTPException(
            status_code=400, detail="Session-ID not found for guest user bad request"
        )

    db_res: str = await credential_db.insert_table(
        "logged_in", (sign_up_credentials.username, sign_up_credentials.password)
    )
    logging.info(db_res)

    # TODO Handle refersh expiry for logged in user
    temp_session: server_types.Session | None = await sh.get_session(
        session_redis, logger, session_id
    )

    if not temp_session:
        return {"server_msg": "user not signed up successfully"}

    new_session: server_types.Session = server_types.Session(
        user=sign_up_credentials.username, is_logged_in=str(True)
    )
    await sh.delete_session(session_redis, logger, session_id) 

    new_session_id : str | None = await sh.add_user(session_redis,logger,new_session)

    if new_session_id:
        res.set_cookie(
                key="Session-ID",
                value=new_session_id,
                httponly=True,
                secure=False, #enable this later
                samesite="lax",
                expires=60,
            )
    logging.info(f" ADDED SESSION WITH SESSION ID {session_id} ")

    return {"server_msg": "user signed up successfully"}


if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
