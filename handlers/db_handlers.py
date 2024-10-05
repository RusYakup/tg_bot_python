import traceback
from asyncpg.pool import Pool
from postgres.database_adapters import create_pool
from fastapi import APIRouter, Depends, Security
from postgres.database_adapters import verify_credentials
from fastapi.security import HTTPBasicCredentials
from postgres.database_adapters import execute
from postgres.sqlfactory import select, update, where, limit, order_by
import logging


log = logging.getLogger(__name__)
router = APIRouter()



@router.get("/users_actions")
async def get_users_actions(chat_id: int = None,
                            from_ts: int = None,
                            until_ts: int = None,
                            limits: int = 1000,
                            credentials: HTTPBasicCredentials = Security(verify_credentials),
                            pool: Pool = Depends(create_pool)):
    """
      Retrieves user actions based on the provided criteria.
      Args:
          chat_id (int): The ID of the chat/user.
          from_ts (int, optional): The starting timestamp. Defaults to None.
          until_ts (int, optional): The ending timestamp. Defaults to None.
          limit (int, optional): The maximum number of results to retrieve. Defaults to 1000.
          credentials (HTTPBasicCredentials, optional): Security credentials. Defaults to Security(verify_credentials).
          pool (Pool, optional): The global database connection pool. Defaults to Depends(create_pool).
      Returns:
          list: The list of user actions retrieved based on the criteria.
      Raises:
          HTTPException: If there is an unauthorized access or an error occurs during retrieval.
      """

    try:
        if from_ts is not None and until_ts is not None:
            sql_select = select("statistic")
            conditions = {
                "chat_id": ("=", chat_id),
                "ts": ("<", from_ts),
                "ts": (">", until_ts),
            }
            query, args = where(sql_select, conditions)
            sql_order_by = order_by(query, "ts", "DESC")
            sql_limit = limit(sql_order_by, limits, args)
            query, args = sql_limit
            res = await execute(pool, query, *args, fetch=True)
            return res
        elif from_ts is not None:
            sql_select = select("statistic")
            conditions = {
                "chat_id": ("=", chat_id),
                "ts": ("<", from_ts),
            }
            query, args = where(sql_select, conditions)
            sql_order_by = order_by(query, "ts", "DESC")
            sql_limit = limit(sql_order_by, limits, args)
            query, args = sql_limit
            res = await execute(pool, query, *args, fetch=True)
            return res
        elif chat_id is not None:
            sql_select = select("statistic")
            sql_where = where(sql_select, {"chat_id": ("=", chat_id)})
            query, args = sql_where
            res = await execute(pool, query, *args, fetch=True)
            return res
        else:
            sql_select = select("statistic", ["DISTINCT ON (chat_id) *"])  ######
            sql_order = order_by(sql_select, "chat_id", "DESC")
            res = await execute(pool, sql_order, fetch=True)
            return res

    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.debug(f"Exception traceback:\n{traceback.format_exc()}")


@router.get("/actions_count")
async def get_actions_count(chat_id: int,
                            from_ts: int = None,
                            until_ts: int = None,
                            credentials: HTTPBasicCredentials = Security(verify_credentials),
                            pool: Pool = Depends(create_pool)):
    """
     Retrieves the count of actions based on the provided chat_id.

     Args:
         chat_id (int): The ID of the chat/user.
         from_ts (int, optional): The starting timestamp. Defaults to None.
         until_ts (int, optional): The ending timestamp. Defaults to None.
         credentials (HTTPBasicCredentials, optional): Security credentials. Defaults to Security(verify_credentials).
         pool (Pool, optional): The global database connection pool. Defaults to Depends(create_pool).

     Returns:
         dict: The count of actions based on the provided chat_id.

     Raises:
         HTTPException: If there is an unauthorized access or an error occurs during retrieval.
     """
    try:
        query = (
            "SELECT chat_id, DATE_TRUNC('month', to_timestamp(ts)) AS month, COUNT(*) AS actions_count FROM statistic "
            "WHERE chat_id = $1 GROUP BY chat_id, month")
        args = [chat_id]
        res = await execute(pool, query, *args, fetch=True)
        return res
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.debug(f"Exception traceback:\n{traceback.format_exc()}")
