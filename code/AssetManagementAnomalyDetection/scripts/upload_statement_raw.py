import os
import sys
from typing import Any, Dict, List

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from pathlib import Path


def parse_value(value: str, value_type: str) -> Any:
    """Parse CSV value based on expected type."""
    if value is None or value == '' or value == 'NULL':
        return None

    if value_type in ['int', 'float']:
        try:
            if value_type == 'int':
                return int(float(value))  # Handle cases like "375.0"
            else:
                return float(value)
        except (ValueError, TypeError):
            return None
    elif value_type == 'date':
        # Keep date as string for simplicity (Azure SQL will handle conversion)
        return value if value != 'NULL' else None
    else:  # string
        # Remove quotes and handle special characters
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        return value


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
    # Resolve CSV path robustly regardless of repo layout changes
    # This script lives in code/AssetManagementAnomalyDetection/scripts/
    # CSV is expected at code/statement-data.csv
    scripts_dir = Path(__file__).resolve().parent
    code_dir = scripts_dir.parents[1]
    csv_path = str(code_dir / 'statement-data.csv')
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found at {csv_path}")

    engine = create_engine(build_azure_uri(), fast_executemany=True)

    # Create table only if it doesn't exist
    create_tables_sql = """
    -- Create table with proper structure if it doesn't exist
    IF OBJECT_ID('dbo.statement_raw','U') IS NULL
    CREATE TABLE dbo.statement_raw (
        id INT PRIMARY KEY,
        property_alias NVARCHAR(100),
        date NVARCHAR(20),
        period_start NVARCHAR(20),
        period_end NVARCHAR(20),
        rent FLOAT,
        management_fee FLOAT,
        repair FLOAT,
        deposit FLOAT,
        misc FLOAT,
        note NVARCHAR(MAX),
        total FLOAT,
        payment_date NVARCHAR(20)
    );
    """

    with engine.begin() as conn:
        # Create table with proper schema
        print("Creating structured table dbo.statement_raw...")
        conn.execute(text(create_tables_sql))

        # Prepare insert statement for structured data
        insert_sql = text("""
            INSERT INTO dbo.statement_raw
            (id, property_alias, date, period_start, period_end, rent,
             management_fee, repair, deposit, misc, note, total, payment_date)
            VALUES
            (:id, :property_alias, :date, :period_start, :period_end, :rent,
             :management_fee, :repair, :deposit, :misc, :note, :total, :payment_date)
        """)

        # Read and parse CSV
        print(f"Reading CSV from {csv_path}...")
        batch: List[Dict[str, Any]] = []
        batch_size = 100
        total = 0

        with open(csv_path, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                # Split CSV line (handle quoted commas)
                parts = []
                current = []
                in_quotes = False

                for char in line:
                    if char == '"':
                        in_quotes = not in_quotes
                        current.append(char)
                    elif char == ',' and not in_quotes:
                        parts.append(''.join(current))
                        current = []
                    else:
                        current.append(char)
                parts.append(''.join(current))  # Don't forget the last part

                if len(parts) != 13:
                    print(f"Warning: Line {line_num} has {len(parts)} fields instead of 13, skipping")
                    continue

                # Parse fields according to schema
                # Handle BOM in first field if this is the first line
                if line_num == 1 and parts[0].startswith('\ufeff'):
                    parts[0] = parts[0][1:]  # Remove BOM character

                record = {
                    'id': parse_value(parts[0], 'int'),
                    'property_alias': parse_value(parts[1], 'string'),
                    'date': parse_value(parts[2], 'date'),
                    'period_start': parse_value(parts[3], 'date'),
                    'period_end': parse_value(parts[4], 'date'),
                    'rent': parse_value(parts[5], 'float'),
                    'management_fee': parse_value(parts[6], 'float'),
                    'repair': parse_value(parts[7], 'float'),
                    'deposit': parse_value(parts[8], 'float'),
                    'misc': parse_value(parts[9], 'float'),
                    'note': parse_value(parts[10], 'string'),
                    'total': parse_value(parts[11], 'float'),
                    'payment_date': parse_value(parts[12], 'date')
                }

                # Skip rows with NULL id
                if record['id'] is None:
                    print(f"Warning: Line {line_num} has NULL id, skipping: {parts[0]}")
                    continue

                batch.append(record)

                # Insert in batches
                if len(batch) >= batch_size:
                    conn.execute(insert_sql, batch)
                    total += len(batch)
                    print(f"Inserted {total} records...")
                    batch.clear()

        # Insert remaining records
        if batch:
            conn.execute(insert_sql, batch)
            total += len(batch)

    print(f"\n✅ Successfully uploaded {total} structured records to Azure dbo.statement_raw")
    print("\nThe data is now properly structured with schema:")
    print("id, property_alias, date, period_start, period_end, rent, management_fee,")
    print("repair, deposit, misc, note, total, payment_date")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

