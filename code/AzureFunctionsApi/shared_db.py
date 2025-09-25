import os
from sqlalchemy import create_engine


def build_tds_uri() -> str:
    server = os.getenv('AZURE_SQL_SERVER')
    database = os.getenv('AZURE_SQL_DATABASE')
    username = os.getenv('AZURE_SQL_USERNAME')
    password = os.getenv('AZURE_SQL_PASSWORD')
    return (
        f"mssql+pytds://{username}:{password}@{server}.database.windows.net:1433/{database}?autocommit=True"
    )


_engine = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(build_tds_uri(), pool_pre_ping=True)
    return _engine
