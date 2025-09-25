import azure.functions as func
import json
from sqlalchemy import text
from shared_db import get_engine


async def main(req: func.HttpRequest) -> func.HttpResponse:
    limit_q = req.params.get('limit', '5')
    try:
        limit = max(1, min(int(limit_q), 100))
    except Exception:
        limit = 5
    try:
        with get_engine().connect() as conn:
            rows = conn.execute(text(f"SELECT TOP {limit} id, line FROM dbo.statement_raw ORDER BY id"))
            cols = rows.keys()
            data = [dict(zip(cols, r)) for r in rows]
        return func.HttpResponse(
            body=json.dumps(data),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        return func.HttpResponse(str(e), status_code=500)

