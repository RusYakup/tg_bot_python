import pytest

from postgres.sqlfactory import select, where, order_by, limit, group_by, delete, insert, update


def test_select():
    fields = ["chat_id, city, last_name"]
    assert select("users", fields) == "SELECT chat_id, city, last_name FROM users"
    assert select("users", []) == "SELECT * FROM users"


def test_delete():
    assert delete("users_table") == "DELETE FROM users_table"


def test_where():
    sql = "SELECT chat_id, city FROM users"
    fields = {
        "chat_id": ("=", "1809"),
        "city": ("=", "Kazan"),
    }
    assert where(sql, fields) == ("SELECT chat_id, city FROM users WHERE chat_id = $1 AND city = $2", ["1809", "Kazan"])


def test_limit():
    sql = "SELECT * FROM users"
    args = ["1809", "Kazan"]
    assert limit(sql, 10, args) == ("SELECT * FROM users LIMIT $3", ["1809", "Kazan", 10])




def test_order_by():
    assert order_by("SELECT * FROM users", "chat_id", "DESC") == "SELECT * FROM users ORDER BY chat_id DESC"


def test_group_by():
    sql = "SELECT chat_id FROM users"
    assert group_by(sql, ["chat_id", "city"]) == "SELECT chat_id FROM users GROUP BY chat_id, city"
    assert group_by(sql, ["chat_id"]) == "SELECT chat_id FROM users GROUP BY chat_id"


def test_update():
    fields = {
        "city": "Moskva",
        "date_difference": "waiting_value", }
    assert update("users", fields) == ("UPDATE users SET city = $1, date_difference = $2", ["Moskva", "waiting_value"])


def test_insert():
    """
    Tests the insert function in the sqlfactory module.

    The following tests are performed:

    1. A basic insert statement with three fields.
    2. An insert statement with an on conflict clause.
    3. An insert statement with an on conflict clause and a do update clause with a single field.
    """
    table = "users"
    fields = {
        "chat_id": "1809",
        "city": "Kazan",
        "last_name": "Yakupov",
    }
    assert insert(table, fields) == ('INSERT INTO users (chat_id, city, last_name) VALUES ($1, $2, $3)', ['1809', 'Kazan', 'Yakupov'])
    assert insert(table, fields,
                  on_conflict="chat_id") == ('INSERT INTO users (chat_id, city, last_name) VALUES ($1, $2, $3)', ['1809', 'Kazan', 'Yakupov'])

    assert insert(table, fields, on_conflict="chat_id", do_update=True, update_fields=[
        "city"]) == ('INSERT INTO users (chat_id, city, last_name) VALUES ($1, $2, $3) ON CONFLICT (chat_id) DO UPDATE SET city = EXCLUDED.city', ['1809', 'Kazan', 'Yakupov'])

    table = "users"
    fields = {
        "chat_id": "1809",
        "city": "Kazan",
        "last_name": "Yakupov",
    }
    assert insert(table, fields) == ('INSERT INTO users (chat_id, city, last_name) VALUES ($1, $2, $3)', ['1809', 'Kazan', 'Yakupov'])
    assert insert(table, fields,
                  on_conflict="chat_id") == ('INSERT INTO users (chat_id, city, last_name) VALUES ($1, $2, $3)', ['1809', 'Kazan', 'Yakupov'])

    assert insert(table, fields, on_conflict="chat_id", do_update=True, update_fields=[
        "city"]) == ('INSERT INTO users (chat_id, city, last_name) VALUES ($1, $2, $3) ON CONFLICT (chat_id) DO UPDATE SET city = EXCLUDED.city', ['1809', 'Kazan', 'Yakupov'])
