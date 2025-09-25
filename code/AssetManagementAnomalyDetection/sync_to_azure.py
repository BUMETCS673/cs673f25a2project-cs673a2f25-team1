import os
from typing import List, Dict, Any

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
	# Note: plus signs in query params must be URL-encoded as + in SQLAlchemy URL string
	return (
		f"mssql+pyodbc://{username}:{password}@{server}.database.windows.net:1433/{database}"
		f"?driver=ODBC+Driver+17+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no&Connection+Timeout=30"
	)


def fetch_all_rows(engine: Engine, table_name: str) -> List[Dict[str, Any]]:
	with engine.connect() as conn:
		rows = conn.execute(text(f"SELECT * FROM {table_name}"))
		columns = rows.keys()
		return [dict(zip(columns, row)) for row in rows]


def truncate_table(conn, table_name: str) -> None:
	# Use DELETE for safety due to possible FK constraints
	conn.execute(text(f"DELETE FROM {table_name}"))


def insert_with_identity(conn, table_name: str, rows: List[Dict[str, Any]]) -> None:
	if not rows:
		return
	columns = list(rows[0].keys())
	columns_sql = ", ".join(f"[{c}]" for c in columns)
	params_sql = ", ".join(f":{c}" for c in columns)
	conn.execute(text(f"SET IDENTITY_INSERT {table_name} ON"))
	insert_sql = text(f"INSERT INTO {table_name} ({columns_sql}) VALUES ({params_sql})")
	# Batch insert
	conn.execute(insert_sql, rows)
	conn.execute(text(f"SET IDENTITY_INSERT {table_name} OFF"))


def main() -> None:
	project_root = os.path.dirname(os.path.abspath(__file__))
	local_db_path = os.path.join(project_root, 'instance', 'asset_management.db')
	if not os.path.exists(local_db_path):
		raise FileNotFoundError(f"Local SQLite DB not found at {local_db_path}")

	local_engine = create_engine(f"sqlite:///{local_db_path}")
	azure_engine = create_engine(build_azure_uri(), fast_executemany=True)

	# Order matters due to FK constraints
	tables_in_order = [
		'portfolios',
		'assets',
		'fees',
		'anomalies',
	]

	# Fetch from local first
	local_data: Dict[str, List[Dict[str, Any]]] = {}
	for t in tables_in_order:
		local_data[t] = fetch_all_rows(local_engine, t)
		print(f"Fetched {len(local_data[t])} rows from local {t}")

	# Push to Azure
	with azure_engine.begin() as conn:
		# Disable constraints during load (defer checks where possible)
		# Not all constraints can be disabled; we rely on correct ordering
		for t in tables_in_order[::-1]:
			# Clear child tables first then parents
			print(f"Clearing Azure table {t}...")
			truncate_table(conn, t)

		for t in tables_in_order:
			rows = local_data[t]
			print(f"Inserting {len(rows)} rows into Azure {t}...")
			insert_with_identity(conn, t, rows)

	print("Sync completed successfully.")


if __name__ == '__main__':
	main()
