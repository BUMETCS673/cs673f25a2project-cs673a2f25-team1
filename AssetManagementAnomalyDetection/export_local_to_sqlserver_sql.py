import os
import sqlite3
from datetime import date, datetime
from typing import Any, Dict, List, Tuple

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SQLITE_PATH = os.path.join(PROJECT_ROOT, 'instance', 'asset_management.db')
OUTPUT_SQL = os.path.join(PROJECT_ROOT, 'azure-deployment', 'azure_sync.sql')

TABLES = [
	'portfolios',
	'assets',
	'fees',
	'anomalies',
]

DDL = {
	'portfolios': (
		"""
		IF OBJECT_ID('dbo.portfolios','U') IS NULL
		CREATE TABLE dbo.portfolios (
			id INT IDENTITY(1,1) PRIMARY KEY,
			name NVARCHAR(100) NOT NULL,
			manager NVARCHAR(100) NOT NULL,
			total_assets FLOAT NOT NULL,
			created_at DATETIME2 DEFAULT GETUTCDATE()
		);
		"""
	),
	'assets': (
		"""
		IF OBJECT_ID('dbo.assets','U') IS NULL
		CREATE TABLE dbo.assets (
			id INT IDENTITY(1,1) PRIMARY KEY,
			portfolio_id INT NOT NULL,
			symbol NVARCHAR(10) NOT NULL,
			name NVARCHAR(100) NOT NULL,
			quantity FLOAT NOT NULL,
			purchase_price FLOAT NOT NULL,
			current_price FLOAT NULL,
			purchase_date DATE NOT NULL,
			FOREIGN KEY (portfolio_id) REFERENCES dbo.portfolios(id)
		);
		"""
	),
	'fees': (
		"""
		IF OBJECT_ID('dbo.fees','U') IS NULL
		CREATE TABLE dbo.fees (
			id INT IDENTITY(1,1) PRIMARY KEY,
			portfolio_id INT NOT NULL,
			amount FLOAT NOT NULL,
			date DATE NOT NULL,
			fee_type NVARCHAR(50) NOT NULL,
			description NVARCHAR(MAX) NULL,
			FOREIGN KEY (portfolio_id) REFERENCES dbo.portfolios(id)
		);
		"""
	),
	'anomalies': (
		"""
		IF OBJECT_ID('dbo.anomalies','U') IS NULL
		CREATE TABLE dbo.anomalies (
			id INT IDENTITY(1,1) PRIMARY KEY,
			portfolio_id INT NOT NULL,
			fee_id INT NOT NULL,
			anomaly_score FLOAT NOT NULL,
			detected_at DATETIME2 DEFAULT GETUTCDATE(),
			reviewed BIT DEFAULT 0,
			FOREIGN KEY (portfolio_id) REFERENCES dbo.portfolios(id),
			FOREIGN KEY (fee_id) REFERENCES dbo.fees(id)
		);
		"""
	),
}


def escape_sql_value(value: Any) -> str:
	if value is None:
		return 'NULL'
	if isinstance(value, (int, float)):
		return str(value)
	if isinstance(value, (datetime, date)):
		return f"'{value.isoformat()}'"
	# Treat as string; escape single quotes
	s = str(value).replace("'", "''")
	return f"'{s}'"


def get_table_rows(conn: sqlite3.Connection, table: str) -> Tuple[List[str], List[Tuple[Any, ...]]]:
	cur = conn.execute(f'SELECT * FROM {table}')
	columns = [d[0] for d in cur.description]
	rows = cur.fetchall()
	return columns, rows


def main() -> None:
	if not os.path.exists(SQLITE_PATH):
		raise FileNotFoundError(f"SQLite DB not found at {SQLITE_PATH}")

	os.makedirs(os.path.dirname(OUTPUT_SQL), exist_ok=True)

	with sqlite3.connect(SQLITE_PATH) as conn, open(OUTPUT_SQL, 'w', encoding='utf-8') as out:
		out.write("-- Generated SQL Server sync script from local SQLite data\n")
		out.write("SET NOCOUNT ON;\nGO\n\n")

		# Ensure schema exists
		for t in TABLES:
			out.write(DDL[t].strip() + "\nGO\n\n")

		# Clear tables in FK-safe order (children first)
		for t in reversed(TABLES):
			out.write(f"DELETE FROM dbo.{t};\nGO\n")
		out.write("\n")

		# Insert data preserving IDs
		for t in TABLES:
			cols, rows = get_table_rows(conn, t)
			if not rows:
				continue
			cols_sql = ', '.join(f'[{c}]' for c in cols)
			out.write(f"SET IDENTITY_INSERT dbo.{t} ON;\n")
			for r in rows:
				vals_sql = ', '.join(escape_sql_value(v) for v in r)
				out.write(f"INSERT INTO dbo.{t} ({cols_sql}) VALUES ({vals_sql});\n")
			out.write(f"SET IDENTITY_INSERT dbo.{t} OFF;\nGO\n\n")

	print(f"Wrote SQL sync script to {OUTPUT_SQL}")


if __name__ == '__main__':
	main()
