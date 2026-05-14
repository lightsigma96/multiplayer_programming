'''SHOULD NOT BE EXPOSED TO CLIENT THROUGH SERVER OR IN ANY WAY, HANDLE SECURITY ISSUES IF EXPOSED'''

import sqlite3
from sqlite3.dbapi2 import Cursor
import sys
import pathlib
from typing import Tuple,List
import os

curr_dir = pathlib.Path(__file__).resolve().parent
external_dir = curr_dir.parent
sys.path.append(str(external_dir))

import server_types

class DB_Handler:
    def __init__(self, db_name : str):
        self.db_name = db_name 

        self.con = sqlite3.connect(db_name)
        self.cursor : Cursor = self.con.cursor() 

    def create_table(self, table_schema : server_types.Schema) -> str:
        try: 
            colmuns : List[str] = [f"{k} {v}" for k,v in table_schema.columns]

            colmun_str : str = ", ".join(colmuns) 
        
            query : str = f"CREATE TABLE IF NOT EXISTS {table_schema.table_name} ({colmun_str}) STRICT"
            
            self.cursor.execute(query)
            return f"table created in {self.db_name}"
        except Exception as e:
            return str(e)
    
    async def insert_table(self, table_name : str, column_values : Tuple[str,str]) -> str:

        try:
            placeholders = ", ".join(["?"] * len(column_values))
            query : str = f"INSERT INTO {table_name} VALUES ({placeholders})"

            self.cursor.execute(query, column_values)
            self.con.commit()
            return f"added entry correctly in {table_name}"
        except Exception as e:
            return str(e)
            
