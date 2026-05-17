from pydantic import BaseModel
from typing import Dict, List, Tuple

## Used by server
class SignupCredentials(BaseModel):
    username: str
    password: str

class Schema(BaseModel):
    table_name: str
    columns: List[Tuple[str, str]]

## Value that each session id holds in Redis, session id is obtained by server through req object so it is not included here 
class Session(BaseModel):
    user: str
    is_logged_in: int
