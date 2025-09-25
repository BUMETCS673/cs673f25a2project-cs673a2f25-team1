import azure.functions as func
import json
from sqlalchemy import text
from shared_db import get_engine


async def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        with get_engine().connect() as conn:
            rows = conn.execute(text("SELECT id, name, manager, total_assets FROM dbo.portfolios"))
            data = [dict(zip(rows.keys(), r)) for r in rows]
        return func.HttpResponse(
            body=json.dumps(data),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        return func.HttpResponse(str(e), status_code=500)

