from decorators.decorators import log_database_query
from postgres.sqlfactory import (select, where, order_by, limit, group_by)
from postgres.database_adapters import execute_query
from asyncpg import Pool, Record
import logging
import traceback
from prometheus.couters import count_general_errors, instance_id

log = logging.getLogger(__name__)


@log_database_query
async def execute_users_actions(pool: Pool, chat_id: int = None, from_ts: int = None, until_ts: int = None,
                                limits: int = 1000) -> [Record | int | None]:
    if pool is None:
        raise ValueError("Pool is None")

    conditions = {}
    if chat_id is not None:
        conditions["chat_id"] = ("=", chat_id)
    if from_ts is not None:
        conditions["ts"] = (">", from_ts)
    if until_ts is not None:
        conditions["ts"] = ("<", until_ts)
    try:
        sql_select = select("statistic", [])
        query, args = where(sql_select, conditions)  #
        query = order_by(query, "ts", "DESC")
        query, args = limit(query, limits, args)

    except Exception as e:
        log.error("execute_users_actions: An error occurred: %s", str(e))
        log.debug(f"execute_users_actions: Exception traceback: \n {traceback.format_exc()}")
        raise
    try:
        res = await execute_query(pool, query, *args, fetch=True)
    except Exception as e:
        log.error("execute_users_actions:An error occurred: %s", str(e))
        log.debug(f"execute_users_actions: Exception traceback: \n {traceback.format_exc()}")
        count_general_errors.labels(instance=instance_id).inc()
        raise

    return res


@log_database_query
async def execute_actions_count(pool: Pool, chat_id: int):
    """ SELECT chat_id, DATE_TRUNC('month', to_timestamp(ts)) AS month, COUNT(*) AS actions_count FROM statistic
    WHERE chat_id = $1 GROUP BY chat_id, month
    """
    try:
        fields_select = [
            "chat_id",
            "DATE_TRUNC('month', to_timestamp(ts)) AS month",
            "COUNT(*) AS actions_count"
        ]
        sql_select = select("statistic", fields_select)
        conditions = {
            "chat_id": ("=", chat_id)
        }
        sql, args = where(sql_select, conditions)

        group_by_columns = ["chat_id", "month"]
        sql_group_by = group_by(sql, group_by_columns)
        res = await execute_query(pool, sql_group_by, *args, fetch=True)
        return res
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.debug(f"Exception traceback:\n{traceback.format_exc()}")
        count_general_errors.labels(instance=instance_id).inc()
