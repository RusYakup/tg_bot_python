import asyncpg
from typing import Union
from asyncpg import Connection
from asyncpg.pool import Pool


class DataBaseClass:
     def __init__(self):
        self.pool: Union[Pool, None] = None


     async def create_pool(self):
        self.pool = await asyncpg.create_pool(
        )
        return self.pool