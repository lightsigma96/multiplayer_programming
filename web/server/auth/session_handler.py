from logging import Logger
from typing import Awaitable, Tuple
from redis.asyncio import Redis
from pydantic import BaseModel

from server_types import Session
from uuid import uuid4

async def add_session(redis_instance: Redis, logger: Logger, sesh: Session, expiry_time : int) -> str | None:
    session_id = str(uuid4())
    redis_key = f"session:{session_id}"

    try:
        await redis_instance.hset(
            redis_key,
            mapping=sesh.model_dump()
        )

        await redis_instance.expire(redis_key, expiry_time)

        return session_id

    except Exception as e:
        logger.info(str(e))
        return None

async def get_session(
    redis_instance: Redis,
    logger: Logger,
    session_id: str
) -> Session | None:

    try:
        data = await redis_instance.hgetall(f"session:{session_id}")

        if not data:
            return None

        return Session(**data)

    except Exception as e:
        logger.error(str(e))
        return None

async def delete_session(redis_instance:Redis, logger: Logger, session_id : str) -> int | None:
    try: 
        return await redis_instance.delete(f"session:{session_id}")
    except Exception as e:
        logger.error(str( e ))
        return None 

async def get_remaining_time(redis_instance:Redis, logger: Logger, session_id : str) -> int | None:
    try: 
        remaining_time_sec : int = await redis_instance.ttl(session_id)
        return remaining_time_sec
    except Exception as e:
        logger.error(e)
        return None


## continous notification might not be needed now
# async def verify_session(redis_instance: Redis):
#     # in server
#     pubsub = redis_instance.pubsub()
#     res = await pubsub.subscribe("__keyevent@0__:expired")
#
#     async for msg in pubsub.listen():
#         print(f"Expired {msg}")
