import logging
from typing import Optional, List
import traceback
from typing import Dict, Tuple, Any
from prometheus.couters import count_general_errors, instance_id

log = logging.getLogger(__name__)


def select(table_name: str, fields: list) -> str:
    """
    Generates a SELECT SQL query based on the provided table name and fields.
    Args:
        table_name (str): The name of the table to select from.
        fields (list): A list of field names to retrieve. If empty, selects all fields.

    Returns:
        str: The constructed SQL query string.

    Raises:
        Exception: If an error occurs during the execution of this function.
    """
    try:
        if fields:
            fields = ", ".join([f"{x}" for x in fields])
        else:
            fields = "*"
        return f"SELECT {fields} FROM {table_name}"
    except Exception as e:
        count_general_errors.labels(instance=instance_id).inc()
        log.error("An error occurred: %s", str(e))
        log.debug(f"Exception traceback:\n{traceback.format_exc()}")


def delete(table_name: str) -> str:
    """
    Generates a DELETE SQL query based on the provided table name.

    Args:
        table_name (str): The name of the table to delete from.

    Returns:
        str: The constructed SQL query string.

    Raises:
        Exception: If an error occurs during the execution of this function.
    """
    try:
        query = f"DELETE FROM {table_name}"
        return query
    except Exception as e:
        count_general_errors.labels(instance=instance_id).inc()
        log.error("An error occurred: %s", str(e))
        log.debug(f"Exception traceback:\n{traceback.format_exc()}")


def where(sql: str, conditions: Dict[str, Tuple[str, Any]]) -> Tuple[str, list]:
    """
    Adds a WHERE clause to an SQL query based on the provided conditions.

    Args:
        sql (str): The base SQL query to which the WHERE clause is added.
        conditions (Dict[str, Tuple[str, Any]]): A dictionary where keys are column names and values are tuples
            containing an operator (e.g., '=', '<', '>') and the corresponding value to filter by.

    Returns:
        Tuple[str, list]: A tuple containing the updated SQL query with the WHERE clause and a list of values
        corresponding to the conditions, to be used as query parameters for safe execution.
    """
    try:
        where_clause = " AND ".join(
            [f"{key} {op} ${i + len(sql.split('$'))}" for i, (key, (op, _)) in enumerate(conditions.items())]
        )
        query = f"{sql} WHERE {where_clause}"
        args = [value for _, (_, value) in conditions.items()]
        return query, args
    except Exception as e:
        count_general_errors.labels(instance=instance_id).inc()
        log.error("An error occurred: %s", str(e))
        log.debug(f"Exception traceback:\n{traceback.format_exc()}")


def limit(sql: str, limit: int, args: List[any]) -> (str, List[any]):
    """
    Adds a LIMIT clause to an SQL query.

    Args:
        sql (str): The base SQL query to which the LIMIT clause is added.
        limit (int): The number of rows to return.
        args (List[any]): The list of query parameters.

    Returns:
        Tuple[str, List[any]]: A tuple containing the updated SQL query with the LIMIT clause and a list of values
        corresponding to the query parameters, to be used for safe execution.
    """
    try:
        new_args = args + [limit]
        return f"{sql} LIMIT ${len(new_args)}", new_args
    except TypeError as e:
        log.error(f"TypeError: {e}")
    except Exception as e:
        count_general_errors.labels(instance=instance_id).inc()
        log.error("An error occurred: %s", str(e))
        log.debug(f"Exception traceback:\n{traceback.format_exc()}")


def order_by(sql: str, column_name: str, sort_order: str) -> str:
    """
    Adds an ORDER BY clause to an SQL query.

    Args:
        sql (str): The base SQL query to which the ORDER BY clause is added.
        column_name (str): The name of the column to sort by.
        sort_order (str): The order in which to sort the column. Must be either "ASC" or "DESC".

    Returns:
        str: The updated SQL query with the ORDER BY clause.

    Raises:
        ValueError: If `sort_order` is not one of "ASC" or "DESC".
    """
    try:
        return f"{sql} ORDER BY {column_name} {sort_order}"
    except Exception as e:
        count_general_errors.labels(instance=instance_id).inc()
        log.error("An error occurred: %s", str(e))
        log.debug(f"Exception traceback:\n{traceback.format_exc()}")


def group_by(sql: str, columns: List[str]) -> str:
    """
    Adds a GROUP BY clause to an SQL query.

    Args:
        sql (str): The base SQL query to which the GROUP BY clause is added.
        columns (List[str]): The names of the columns to group by.

    Returns:
        str: The updated SQL query with the GROUP BY clause.

    Raises:
        Exception: If an error occurs during the execution of this function.
    """
    try:
        group_by_clause = ", ".join(columns)
        return f"{sql} GROUP BY {group_by_clause}"
    except Exception as e:
        count_general_errors.labels(instance=instance_id).inc()
        log.error("An error occurred: %s", str(e))
        log.debug(f"Exception traceback:\n{traceback.format_exc()}")


def update(table_name: str, fields: Dict[str, Any]) -> Tuple[str, List[Any]]:
    """
    Generates an UPDATE query based on the provided table name and fields.

    Args:
        table_name (str): The name of the table to update.
        fields (Dict[str, Any]): A dictionary where keys are column names and values are the corresponding values to
            update.

    Returns:
        Tuple[str, List[Any]]: A tuple containing the generated SQL query and a list of values to be used as query
            parameters for safe execution.

    Raises:
        Exception: If an error occurs during the execution of this function.
    """
    try:
        set_clause = ", ".join([f"{key} = ${i + 1}" for i, key in enumerate(fields)])
        query = f"UPDATE {table_name} SET {set_clause}"
        values = list(fields.values())
        return query, values
    except Exception as e:
        count_general_errors.labels(instance=instance_id).inc()
        log.error("An error occurred: %s", str(e))
        log.debug(f"Exception traceback:\n{traceback.format_exc()}")


def insert(table_name: str, fields: Dict[str, Any], on_conflict: Optional[str] = None,
           update_fields: Optional[List[str]] = None) -> Tuple[str, List[Any]]:
    """
    Generates an INSERT query based on the provided table name and fields.

    Args:
        table_name (str): The name of the table to insert into.
        fields (Dict[str, Any]): A dictionary where keys are column names and values are the corresponding values to
            insert.
        on_conflict (Optional[str]): The name of the column to check for conflicts. If not provided, no conflict clause
            will be added.
        update_fields (Optional[List[str]]): A list of column names to update if a conflict occurs. If not provided, no
            update will be performed.

    Returns:
        Tuple[str, List[Any]]: A tuple containing the generated SQL query and a list of values to be used as query
            parameters for safe execution.

    Raises:
        Exception: If an error occurs during the execution of this function.
    """
    try:
        columns = ", ".join(fields.keys())
        placeholders = ', '.join([f"${i + 1}" for i in range(len(fields))])
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        if on_conflict:
            if update_fields:
                conflict_update = ", ".join(
                    [f"{col} = EXCLUDED.{col}" for col in update_fields]
                )
                sql += f" ON CONFLICT ({on_conflict}) DO UPDATE SET {conflict_update}"
            else:
                sql += f" ON CONFLICT ({on_conflict}) DO NOTHING"
        args = list(fields.values())
        return sql, args

    except Exception as e:
        count_general_errors.labels(instance=instance_id).inc()
        log.error("An error occurred: %s", str(e))
        log.debug(f"Exception traceback:\n{traceback.format_exc()}")
