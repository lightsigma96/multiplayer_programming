from pydantic import BaseModel
from typing import Dict,List,Tuple

class Schema(BaseModel):
    table_name : str
    columns : List[Tuple[str, str]]

class Cookie(BaseModel):
    session_id: str

class Session(BaseModel):
    user : str
    is_logged_in : str

