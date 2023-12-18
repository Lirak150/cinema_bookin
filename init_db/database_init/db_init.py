import psycopg2
from pathlib import Path
from config import PostgresConfig

ddl_dir = "ddl"
models_dir = ["movies", "sessions", "users", "system"]


def init_functions():
    with psycopg2.connect(host=PostgresConfig.db_host, port=PostgresConfig.db_port,
                          user=PostgresConfig.init_user,
                          password=PostgresConfig.init_user_password) as connect:
        connect.autocommit = True
        with connect.cursor() as cur:
            with (Path(__file__).parent / 'init_db.sql').open(mode='r') as public_funcs_fd:
                cur.execute(public_funcs_fd.read())


def init_role():
    with psycopg2.connect(host=PostgresConfig.db_host, port=PostgresConfig.db_port,
                          user=PostgresConfig.init_user,
                          password=PostgresConfig.init_user_password) as connect:
        connect.autocommit = True
        with connect.cursor() as cur:
            cur.execute('CALL create_role(%s::varchar, %s::varchar)',
                        (PostgresConfig.app_user, PostgresConfig.app_user_password))


def init_db():
    connect = None
    try:
        connect = psycopg2.connect(host=PostgresConfig.db_host, port=PostgresConfig.db_port,
                                   user=PostgresConfig.app_user,
                                   password=PostgresConfig.app_user_password,
                                   dbname=PostgresConfig.default_db)
        connect.autocommit = True
        with connect.cursor() as cur:
            cur.execute("CALL create_db(%s::varchar, %s::varchar)", (PostgresConfig.app_db, PostgresConfig.app_user))
    finally:
        if connect:
            connect.close()


def is_db_exists():
    connect = None
    try:
        connect = psycopg2.connect(host=PostgresConfig.db_host, port=PostgresConfig.db_port,
                                   user=PostgresConfig.app_user,
                                   password=PostgresConfig.app_user_password,
                                   dbname=PostgresConfig.default_db)
        connect.autocommit = True
        with connect.cursor() as cur:
            cur.execute("select check_db_exists(%s::varchar)", (PostgresConfig.app_db,))
            exists = cur.fetchone()
            return exists if exists is None else exists[0]
    finally:
        if connect:
            connect.close()


def init_structure():
    with psycopg2.connect(host=PostgresConfig.db_host, port=PostgresConfig.db_port,
                          user=PostgresConfig.app_user,
                          password=PostgresConfig.app_user_password,
                          dbname=PostgresConfig.app_db) as connect:
        connect.autocommit = True
        with connect.cursor() as cur:
            current_dir = Path(__file__).parent.parent / "domain_models" / ddl_dir
            for model in current_dir.glob("*"):
                current_model = current_dir / model
                if current_model.is_file():
                    with current_model.open(mode="rt") as current_model_fd:
                        cur.execute(current_model_fd.read())
            cur.execute("CALL create_ddl()")
            for dm in models_dir:
                current_dir = Path(__file__).parent.parent / "domain_models" / dm
                for model in current_dir.glob("*"):
                    current_model = current_dir / model
                    if current_model.is_file():
                        with current_model.open(mode="rt") as current_model_fd:
                            cur.execute(current_model_fd.read())
