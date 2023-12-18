import datetime
from typing import Optional
import psycopg2
import os
import subprocess
from config import PostgresConfig


def db_connect() -> psycopg2._psycopg.connection:
    conn_params = dict(host=PostgresConfig.db_host, port=PostgresConfig.db_port,
                       user=PostgresConfig.app_user,
                       password=PostgresConfig.app_user_password,
                       dbname=PostgresConfig.app_db)
    return psycopg2.connect(**conn_params)


def register_user(user_name: str, user_pass: str, user_role: str) -> bool:
    with db_connect() as connect:
        connect.autocommit = True
        with connect.cursor() as cur:
            cur.execute("select register_user(%s::varchar, %s::varchar, %s::varchar)",
                        (user_name, user_pass, user_role))
            return cur.fetchone()[0]


def login_user(user_name: str, user_pass: str) -> bool:
    with db_connect() as connect:
        connect.autocommit = True
        with connect.cursor() as cur:
            cur.execute("select login_user(%s::varchar, %s::varchar)",
                        (user_name, user_pass))
            return cur.fetchone()[0]


def get_user_role(user_name: str) -> str:
    with db_connect() as connect:
        connect.autocommit = True
        with connect.cursor() as cur:
            cur.execute("select get_user_role(%s::varchar)",
                        (user_name,))
            return cur.fetchone()[0]


def get_genres(movie_id: Optional[int] = None) -> dict[str, int]:
    with db_connect() as connect:
        connect.autocommit = True
        with connect.cursor() as cur:
            cur.execute("select * from get_genres(%s::int)", (movie_id,))
            result = cur.fetchall()
            return {item[1]: item[0] for item in result}


def get_actors(movie_id: Optional[int] = None) -> dict[tuple[str, str], int]:
    with db_connect() as connect:
        connect.autocommit = True
        with connect.cursor() as cur:
            cur.execute("select * from get_actors(%s::int)", (movie_id,))
            result = cur.fetchall()
            return {item[1:]: item[0] for item in result}


def add_film(film_name: str, release_year: int, genre_id: int, actors_ids: list[int]) -> bool:
    with db_connect() as connect:
        connect.autocommit = True
        with connect.cursor() as cur:
            cur.execute("select add_new_film(%s::varchar, %s::int, %s::int, %s::int[])",
                        (film_name, release_year, genre_id, actors_ids))
            result = cur.fetchone()
            return result[0]


def add_actor(first_name: str, last_name: str) -> bool:
    with db_connect() as connect:
        connect.autocommit = True
        with connect.cursor() as cur:
            cur.execute("select add_new_actor(%s::varchar, %s::varchar)",
                        (first_name, last_name))
            result = cur.fetchone()
            return result[0]


def add_genre(genre: str) -> bool:
    with db_connect() as connect:
        connect.autocommit = True
        with connect.cursor() as cur:
            cur.execute("select add_new_genre(%s::varchar)",
                        (genre,))
            result = cur.fetchone()
            return result[0]


def add_new_hall(hall_name: str, seats_count: int) -> bool:
    with db_connect() as connect:
        with connect.cursor() as cur:
            connect.autocommit = True
            cur.execute("select add_new_hall(%s::varchar, %s::smallint)",
                        (hall_name, seats_count))
            result = cur.fetchone()
            return result[0]


def add_new_session(movie_name: str, start_time: datetime.datetime, hall_name: str, price: float) -> bool:
    with db_connect() as connect:
        connect.autocommit = True
        with connect.cursor() as cur:
            cur.execute("select add_new_session(%s::varchar, %s::timestamp, %s::varchar, %s::decimal)",
                        (movie_name, start_time, hall_name, price))
            result = cur.fetchone()
            return result[0]


def get_bought_tickets_today() -> int:
    with db_connect() as connect:
        connect.autocommit = True
        with connect.cursor() as cur:
            cur.execute("select get_bought_tickets_today()")
            result = cur.fetchone()
            return result[0]


def get_movies() -> dict[str, tuple[int, int]]:
    with db_connect() as connect:
        connect.autocommit = True
        with connect.cursor() as cur:
            cur.execute("select * from get_movies()")
            result = cur.fetchall()
            return {(item[1]): (item[0], item[2]) for item in result}


def delete_movie(movie_id: int) -> bool:
    with db_connect() as connect:
        connect.autocommit = True
        with connect.cursor() as cur:
            try:
                cur.execute("call delete_movie(%s::int)", (movie_id,))
                return True
            except psycopg2.errors.ForeignKeyViolation as exc:
                return False


def update_movie(movie_id: str, release_year: int, genre_id: int, actors_ids: list[int]) -> bool:
    with db_connect() as connect:
        connect.autocommit = True
        with connect.cursor() as cur:
            cur.execute("call update_movie(%s::int, %s::int, %s::int, %s::int[])",
                        (movie_id, release_year, genre_id, actors_ids))


def get_available_sessions():
    with db_connect() as connect:
        connect.autocommit = True
        with connect.cursor() as cur:
            cur.execute("select * from get_available_sessions()")
            result = cur.fetchall()
            return {(item[2]): (item[0], item[1], item[3], item[4], item[5], item[6]) for item in result}


def get_tickets(user_name: str):
    with db_connect() as connect:
        connect.autocommit = True
        with connect.cursor() as cur:
            cur.execute("select * from get_tickets(%s::varchar)", (user_name,))
            result = cur.fetchall()
            return result


def buy_ticket(session_id: int, user_name):
    with db_connect() as connect:
        connect.autocommit = True
        with connect.cursor() as cur:
            cur.execute("call buy_ticket(%s::int, %s::varchar)",
                        (session_id, user_name))


def get_halls():
    with db_connect() as connect:
        connect.autocommit = True
        with connect.cursor() as cur:
            cur.execute("select * from get_halls()")
            result = cur.fetchall()
            return [item[0] for item in result]


def truncate_tables():
    with db_connect() as connect:
        connect.autocommit = True
        with connect.cursor() as cur:
            cur.execute("call truncate_all_tables()")


def truncate_movies():
    with db_connect() as connect:
        connect.autocommit = True
        with connect.cursor() as cur:
            cur.execute("select truncate_movies()")
            return cur.fetchone()[0]


def drop_db():
    command = f"dropdb -h {PostgresConfig.db_host} -p {PostgresConfig.db_port} -U {PostgresConfig.app_user} -e {PostgresConfig.app_db} --if-exists --force"
    os.system(command)
