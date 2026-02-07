from fastapi import APIRouter, Depends, HTTPException, Query

from api.dependencies import verify_api_key, get_api_db, APIDBManager

router = APIRouter(prefix="/api", tags=["People"], dependencies=[Depends(verify_api_key)])


@router.get("/faculty")
def list_faculty(
    department_id: str | None = Query(default=None, description="Filter by department ID"),
    name: str | None = Query(default=None, description="Search by name (partial match)"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: APIDBManager = Depends(get_api_db),
):
    query = db.client.table("faculty_members").select("*, departments(name, code)")
    if department_id:
        query = query.eq("department_id", department_id)
    if name:
        query = query.ilike("name", f"%{name}%")
    query = query.range(offset, offset + limit - 1)
    response = query.execute()
    return {"data": response.data, "count": len(response.data)}


@router.get("/faculty/{faculty_id}")
def get_faculty_member(
    faculty_id: str,
    db: APIDBManager = Depends(get_api_db),
):
    response = (
        db.client.table("faculty_members")
        .select("*, departments(name, code)")
        .eq("id", faculty_id)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Faculty member not found")
    return {"data": response.data[0]}


@router.get("/governance")
def list_governance(
    body: str | None = Query(
        default=None,
        description="Filter by governance body (academic_council, board_of_trustees, syndicate)",
    ),
    db: APIDBManager = Depends(get_api_db),
):
    query = db.client.table("governance_members").select("*")
    if body:
        query = query.eq("body", body)
    response = query.execute()
    return {"data": response.data, "count": len(response.data)}


@router.get("/alumni")
def list_alumni(db: APIDBManager = Depends(get_api_db)):
    response = db.client.table("notable_alumni").select("*").execute()
    return {"data": response.data, "count": len(response.data)}
