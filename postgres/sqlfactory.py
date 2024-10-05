import logging
from typing import Optional, List, Dict
import traceback
from typing import Dict, Tuple, Any

log = logging.getLogger(__name__)



def select(table_name: str, fields=None) -> (str):
    if fields:
        fields = ", ".join([f"{x}" for x in fields])
    else:
        fields = "*"
    return f"SELECT {fields} FROM {table_name}"

def where(sql: str, conditions: Dict[str, Tuple[str, Any]], start_index: int = 1) -> Tuple[str, list]:
    """
    Формирует SQL-запрос с условием WHERE из предоставленных условий.
    :param sql: начальная часть SQL-запроса (до WHERE)
    :param conditions: условия в формате {колонка: (оператор, значение)}
    :param start_index: стартовый индекс для параметров запроса
    :return: строка запроса и список аргументов
    """
    try:
        where_clause = " AND ".join(
            [f"{key} {op} ${i + start_index}" for i, (key, (op, _)) in enumerate(conditions.items())]
        )
        query = f"{sql} WHERE {where_clause}"
        args = [value for _, (_, value) in conditions.items()]
        return query, args
    except Exception as e:
        log.error(f"An error occurred during where clause generation: {e}")
        log.debug("Exception traceback:", traceback.format_exc())


def limit(sql: str, limit: int, args: List[any]) -> (str, List[any]):
    new_args = args + [limit]
    return f"{sql} LIMIT ${len(new_args)}", new_args


def order_by(sql: str, column_name: str, sort_order: str) -> str:
    return f"{sql} ORDER BY {column_name} {sort_order}"


def update(table_name: str, fields: dict) -> str:
    set_clause = ", ".join([f"{key} = ${i + 1}" for i, key in enumerate(fields)])
    return f"UPDATE {table_name} SET {set_clause}"