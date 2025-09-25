import os
import csv
from datetime import datetime
from typing import Dict, Any, List, Optional

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


def build_azure_uri() -> str:
    load_dotenv()
    server = os.getenv('AZURE_SQL_SERVER')
    database = os.getenv('AZURE_SQL_DATABASE')
    username = os.getenv('AZURE_SQL_USERNAME')
    password = os.getenv('AZURE_SQL_PASSWORD')
    if not all([server, database, username, password]):
        raise RuntimeError('Missing AZURE_SQL_* environment variables')
    # Allow overriding the ODBC driver via environment variable. Default to v18 if present.
    driver_name = os.getenv('ODBC_DRIVER_NAME') or 'ODBC Driver 18 for SQL Server'
    driver_qs = driver_name.replace(' ', '+')
    return (
        f"mssql+pyodbc://{username}:{password}@{server}.database.windows.net:1433/{database}"
        f"?driver={driver_qs}&Encrypt=yes&TrustServerCertificate=no&Connection+Timeout=30"
    )


def ensure_table(engine: Engine) -> None:
    create_sql = """
    IF OBJECT_ID('dbo.statement_entries','U') IS NULL
    CREATE TABLE dbo.statement_entries (
        id INT IDENTITY(1,1) PRIMARY KEY,
        source_row_id INT NULL,
        property_name NVARCHAR(100) NULL,
        statement_date DATE NULL,
        period_start DATE NULL,
        period_end DATE NULL,
        amount1 FLOAT NULL,
        amount2 FLOAT NULL,
        amount3 FLOAT NULL,
        amount4 FLOAT NULL,
        amount5 FLOAT NULL,
        notes NVARCHAR(MAX) NULL,
        balance FLOAT NULL,
        attachment NVARCHAR(255) NULL,
        raw_csv NVARCHAR(MAX) NULL
    );
    """
    with engine.begin() as conn:
        conn.execute(text(create_sql))


def parse_float(cell: str) -> Optional[float]:
    if cell is None or cell == '' or cell.upper() == 'NULL':
        return None
    try:
        sanitized = cell.replace(',', '').replace('$', '')
        return float(sanitized)
    except Exception:
        return None


def parse_date(cell: str) -> Optional[str]:
    if not cell or cell.upper() == 'NULL':
        return None
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y"):
        try:
            d = datetime.strptime(cell.strip(), fmt).date()
            return d.isoformat()
        except Exception:
            continue
    return None


def read_csv_rows(csv_path: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for line_num, cells in enumerate(reader, start=1):
            cells = (cells + [None] * 13)[:13]
            row: Dict[str, Any] = {
                'source_row_id': int(cells[0]) if cells[0] and str(cells[0]).isdigit() else None,
                'property_name': (cells[1] or None),
                'statement_date': parse_date(cells[2]),
                'period_start': parse_date(cells[3]),
                'period_end': parse_date(cells[4]),
                'amount1': parse_float(cells[5]),
                'amount2': parse_float(cells[6]),
                'amount3': parse_float(cells[7]),
                'amount4': parse_float(cells[8]),
                'amount5': parse_float(cells[9]),
                'notes': (cells[10] or None),
                'balance': parse_float(cells[11]),
                'attachment': (cells[12] or None),
                'raw_csv': ",".join('' if c is None else str(c) for c in cells),
            }
            rows.append(row)
    return rows


def bulk_insert(engine: Engine, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        print('No rows to insert.')
        return
    columns = list(rows[0].keys())
    col_sql = ", ".join(f"[{c}]" for c in columns)
    param_sql = ", ".join(f":{c}" for c in columns)
    insert_stmt = text(f"INSERT INTO dbo.statement_entries ({col_sql}) VALUES ({param_sql})")
    with engine.begin() as conn:
        conn.execute(insert_stmt, rows)


def main() -> None:
    project_root = os.path.dirname(os.path.abspath(__file__))
    # project_root points to .../AssetManagementAnomalyDetection/scripts
    repo_root = os.path.dirname(project_root)
    csv_path = os.path.join(os.path.dirname(repo_root), 'code', 'statement-data.csv')
    if not os.path.exists(csv_path):
        # try within repo_root/code as fallback
        csv_path = os.path.join(repo_root, 'code', 'statement-data.csv')
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found at {csv_path}")

    print(f"Reading CSV from {csv_path} ...")
    rows = read_csv_rows(csv_path)
    print(f"Parsed {len(rows)} rows from CSV")

    # Dry-run if Azure env vars are not configured
    server = os.getenv('AZURE_SQL_SERVER')
    database = os.getenv('AZURE_SQL_DATABASE')
    username = os.getenv('AZURE_SQL_USERNAME')
    password = os.getenv('AZURE_SQL_PASSWORD')
    if not all([server, database, username, password]):
        print('Azure environment variables are not set. Parsed rows only (dry run). Skipping upload.')
        return

    azure_uri = build_azure_uri()
    print('Connecting to Azure SQL...')
    engine = create_engine(azure_uri, fast_executemany=True)
    ensure_table(engine)
    print('Table ensured.')

    print('Inserting rows...')
    bulk_insert(engine, rows)
    print('Ingestion completed successfully.')

if __name__ == '__main__':
    main()
