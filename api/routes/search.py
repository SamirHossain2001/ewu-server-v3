from fastapi import APIRouter, Depends, Query

from api.dependencies import verify_api_key, get_api_db, APIDBManager

router = APIRouter(prefix="/api", tags=["Search"], dependencies=[Depends(verify_api_key)])

SEARCH_TABLES = [
    {"table": "programs", "column": "name", "label": "programs"},
    {"table": "faculty_members", "column": "name", "label": "faculty"},
    {"table": "clubs", "column": "name", "label": "clubs"},
    {"table": "events", "column": "title", "label": "events"},
    {"table": "policies", "column": "name", "label": "policies"},
]


@router.get("/search")
def search(
    q: str = Query(min_length=1, description="Search query"),
    db: APIDBManager = Depends(get_api_db),
):
    results = {}
    pattern = f"%{q}%"

    for cfg in SEARCH_TABLES:
        response = (
            db.client.table(cfg["table"])
            .select("*")
            .ilike(cfg["column"], pattern)
            .limit(10)
            .execute()
        )
        if response.data:
            results[cfg["label"]] = response.data

    total = sum(len(v) for v in results.values())
    return {"data": results, "count": total}
