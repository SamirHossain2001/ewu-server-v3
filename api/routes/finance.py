from fastapi import APIRouter, Depends, Query

from api.dependencies import verify_api_key, get_api_db, APIDBManager

router = APIRouter(prefix="/api", tags=["Finance"], dependencies=[Depends(verify_api_key)])


@router.get("/tuition-fees")
def list_tuition_fees(
    level: str | None = Query(default=None, description="Filter by level (undergraduate/graduate)"),
    db: APIDBManager = Depends(get_api_db),
):
    query = db.client.table("tuition_fees").select("*")
    if level:
        query = query.ilike("level", f"%{level}%")
    response = query.execute()
    return {"data": response.data, "count": len(response.data)}


@router.get("/scholarships")
def list_scholarships(db: APIDBManager = Depends(get_api_db)):
    response = db.client.table("scholarships").select("*").execute()
    return {"data": response.data, "count": len(response.data)}
