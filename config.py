import os
from dotenv import load_dotenv

load_dotenv()


class PostgresConfig:
    init_user = os.getenv("POSTGRES_USER")
    init_user_password = os.getenv("POSTGRES_PASSWORD")
    default_db = os.getenv("POSTGRES_DB")

    app_user = os.getenv("APP_USER")
    app_schema = os.getenv("APP_SCHEMA")
    app_user_password = os.getenv("APP_USER_PASSWORD")
    app_db = os.getenv("APP_DB")

    db_port = os.getenv("DB_PORT")
    db_host = os.getenv("DB_HOST")
