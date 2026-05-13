from typing import Awaitable, Tuple
from redis.asyncio import Redis
from pydantic import BaseModel
from uuid import uuid4

class Session(BaseModel):
    user : str

async def add_user(redis_instance: Redis, user: str) -> str:
    '''Creates a new session'''
    session_id = f"session:{str(uuid4())}"
    session : Session = Session(user= user)

    try:

        await redis_instance.hset(
            session_id,
            mapping= session.model_dump()
        )

        await redis_instance.expire(session_id, 60)

        return session_id

    except Exception as e:
        return str(e)

async def get_all_sessions(redis_instance: Redis):
    return await redis_instance.keys("session:*")

async def get_session(redis_instance: Redis, session_id : str):
    return await redis_instance.get(f"session:{session_id}")

## continous notification might not be needed now
# async def verify_session(redis_instance: Redis):
#     # in server
#     pubsub = redis_instance.pubsub()
#     res = await pubsub.subscribe("__keyevent@0__:expired")
#
#     async for msg in pubsub.listen():
#         print(f"Expired {msg}")
