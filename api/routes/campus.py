from fastapi import APIRouter, Depends, Query

from api.dependencies import verify_api_key, get_api_db, APIDBManager

router = APIRouter(prefix="/api", tags=["Campus"], dependencies=[Depends(verify_api_key)])


@router.get("/clubs")
def list_clubs(db: APIDBManager = Depends(get_api_db)):
    response = db.client.table("clubs").select("*").execute()
    return {"data": response.data, "count": len(response.data)}


@router.get("/events")
def list_events(db: APIDBManager = Depends(get_api_db)):
    response = (
        db.client.table("events")
        .select("*")
        .order("event_date", desc=True)
        .execute()
    )
    return {"data": response.data, "count": len(response.data)}


@router.get("/notices")
def list_notices(
    limit: int = Query(default=50, ge=1, le=500, description="Max records to return"),
    db: APIDBManager = Depends(get_api_db),
):
    response = (
        db.client.table("notices")
        .select("*")
        .order("published_date", desc=True)
        .limit(limit)
        .execute()
    )
    return {"data": response.data, "count": len(response.data)}


@router.get("/helpdesk")
def list_helpdesk(
    category: str | None = Query(default=None, description="Filter by category"),
    db: APIDBManager = Depends(get_api_db),
):
    query = db.client.table("helpdesk_contacts").select("*")
    if category:
        query = query.ilike("category", f"%{category}%")
    response = query.execute()
    return {"data": response.data, "count": len(response.data)}


@router.get("/proctor-schedule")
def list_proctor_schedule(db: APIDBManager = Depends(get_api_db)):
    response = db.client.table("proctor_schedule").select("*").execute()
    return {"data": response.data, "count": len(response.data)}
