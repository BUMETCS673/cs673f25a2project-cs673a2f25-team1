import os
import sys
from typing import Iterable

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


def iter_lines(file_path: str) -> Iterable[str]:
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            yield line.rstrip('\n')


def build_azure_uri() -> str:
    load_dotenv()
    server = os.getenv('AZURE_SQL_SERVER')
    database = os.getenv('AZURE_SQL_DATABASE')
    username = os.getenv('AZURE_SQL_USERNAME')
    password = os.getenv('AZURE_SQL_PASSWORD')
    if not all([server, database, username, password]):
        raise RuntimeError('Missing AZURE_SQL_* environment variables')
    return (
        f"mssql+pyodbc://{username}:{password}@{server}.database.windows.net:1433/{database}"
        f"?driver=ODBC+Driver+17+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no&Connection+Timeout=30"
    )


def main() -> None:
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(os.path.dirname(project_root), 'code', 'statement-data.csv')
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found at {csv_path}")

    engine = create_engine(build_azure_uri(), fast_executemany=True)

    create_table_sql = """
    IF OBJECT_ID('dbo.statement_raw','U') IS NULL
    CREATE TABLE dbo.statement_raw (
        id INT IDENTITY(1,1) PRIMARY KEY,
        line NVARCHAR(MAX) NOT NULL
    );
    """

    with engine.begin() as conn:
        # Ensure table exists
        conn.execute(text(create_table_sql))
        # Clear existing to avoid duplicates
        conn.execute(text("DELETE FROM dbo.statement_raw"))

        # Batch insert lines
        batch: list[dict[str, str]] = []
        batch_size = 1000
        insert_sql = text("INSERT INTO dbo.statement_raw (line) VALUES (:line)")
        total = 0
        for line in iter_lines(csv_path):
            batch.append({"line": line})
            if len(batch) >= batch_size:
                conn.execute(insert_sql, batch)
                total += len(batch)
                batch.clear()
        if batch:
            conn.execute(insert_sql, batch)
            total += len(batch)

    print(f"Uploaded {total} lines from {csv_path} to Azure dbo.statement_raw")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

