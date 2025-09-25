import os
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


def build_azure_uri() -> str:
    load_dotenv()
    server = os.getenv('AZURE_SQL_SERVER')
    database = os.getenv('AZURE_SQL_DATABASE')
    username = os.getenv('AZURE_SQL_USERNAME')
    password = os.getenv('AZURE_SQL_PASSWORD')
    if not all([server, database, username, password]):
        raise RuntimeError('Missing AZURE_SQL_* environment variables')
    driver_name = os.getenv('ODBC_DRIVER_NAME') or 'ODBC Driver 18 for SQL Server'
    driver_qs = driver_name.replace(' ', '+')
    return (
        f"mssql+pyodbc://{username}:{password}@{server}.database.windows.net:1433/{database}?"
        f"driver={driver_qs}&Encrypt=yes&TrustServerCertificate=no&Connection+Timeout=30"
    )


def main() -> None:
    server = os.getenv('AZURE_SQL_SERVER')
    if not server:
        print('Azure env not set; skipping transform.')
        return
    engine = create_engine(build_azure_uri())
    with engine.begin() as conn:
        # Naive mapping: map amount1 to fee amount, statement_date to fee date
        # Requires an existing portfolio with id=1. Adjust as needed.
        conn.execute(text(
            """
            INSERT INTO dbo.fees (portfolio_id, amount, date, fee_type, description)
            SELECT 
                1 AS portfolio_id,
                COALESCE(amount1,0) AS amount,
                TRY_CONVERT(date, statement_date) AS date,
                'management' AS fee_type,
                COALESCE(notes, 'imported from statement_entries') AS description
            FROM dbo.statement_entries
            WHERE amount1 IS NOT NULL AND statement_date IS NOT NULL;
            """
        ))
    print('Transform completed.')


if __name__ == '__main__':
    main()
