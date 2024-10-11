import logging
from typing import Optional, List, Dict
import traceback
from typing import Dict, Tuple, Any

log = logging.getLogger(__name__)


def select(table_name: str, fields: list) -> (str):
    try:
        if fields:
            fields = ", ".join([f"{x}" for x in fields])
        else:
            fields = "*"
        return f"SELECT {fields} FROM {table_name}"
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.debug(f"Exception traceback:\n{traceback.format_exc()}")


def where(sql: str, conditions: Dict[str, Tuple[str, Any]]) -> Tuple[str, list]:
    try:
        where_clause = " AND ".join(
            [f"{key} {op} ${i + len(sql.split('$'))}" for i, (key, (op, _)) in enumerate(conditions.items())]
        )
        query = f"{sql} WHERE {where_clause}"
        args = [value for _, (_, value) in conditions.items()]
        return query, args
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.debug(f"Exception traceback:\n{traceback.format_exc()}")


def limit(sql: str, limit: int, args: List[any]) -> (str, List[any]):
    try:
        new_args = args + [limit]
        return f"{sql} LIMIT ${len(new_args)}", new_args
    except TypeError as e:
        log.error(f"TypeError: {e}")
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.debug(f"Exception traceback:\n{traceback.format_exc()}")


def order_by(sql: str, column_name: str, sort_order: str) -> str:
    try:
        return f"{sql} ORDER BY {column_name} {sort_order}"
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.debug(f"Exception traceback:\n{traceback.format_exc()}")


def group_by(sql: str, columns: List[str]) -> str:
    try:
        group_by_clause = ", ".join(columns)
        return f"{sql} GROUP BY {group_by_clause}"
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.debug(f"Exception traceback:\n{traceback.format_exc()}")


def update(table_name: str, fields: Dict[str, Any]) -> Tuple[str, List[Any]]:
    try:
        set_clause = ", ".join([f"{key} = ${i + 1}" for i, key in enumerate(fields)])
        query = f"UPDATE {table_name} SET {set_clause}"
        values = list(fields.values())
        return query, values
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.debug(f"Exception traceback:\n{traceback.format_exc()}")
def insert(table_name: str, fields: Dict[str, Any], on_conflict: Optional[str] = None) -> Tuple[str, List[Any]]:
    try:
        columns = ", ".join(fields.keys())
        placeholders = ', '.join([f"${i + 1}" for i in range(len(fields))])
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        if on_conflict:
            sql += f" ON CONFLICT ({on_conflict}) DO NOTHING"
        args = list(fields.values())
        return sql, args
    except Exception as e:
        log.error("An error occurred: %s", str(e))
        log.debug(f"Exception traceback:\n{traceback.format_exc()}")
