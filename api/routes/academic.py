from fastapi import APIRouter, Depends, HTTPException, Query

from api.dependencies import verify_api_key, get_api_db, APIDBManager

router = APIRouter(prefix="/api", tags=["Academic"], dependencies=[Depends(verify_api_key)])


@router.get("/departments")
def list_departments(
    faculty: str | None = Query(default=None, description="Filter by faculty name"),
    db: APIDBManager = Depends(get_api_db),
):
    query = db.client.table("departments").select("*")
    if faculty:
        query = query.ilike("faculty", f"%{faculty}%")
    response = query.execute()
    return {"data": response.data, "count": len(response.data)}


@router.get("/programs")
def list_programs(
    degree_type: str | None = Query(default=None, description="Filter by degree type"),
    department_id: str | None = Query(default=None, description="Filter by department ID"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: APIDBManager = Depends(get_api_db),
):
    query = db.client.table("programs").select("*, departments(name, code)")
    if degree_type:
        query = query.eq("degree_type", degree_type)
    if department_id:
        query = query.eq("department_id", department_id)
    query = query.range(offset, offset + limit - 1)
    response = query.execute()
    return {"data": response.data, "count": len(response.data)}


@router.get("/programs/{program_id}")
def get_program(
    program_id: str,
    db: APIDBManager = Depends(get_api_db),
):
    response = (
        db.client.table("programs")
        .select("*, departments(name, code)")
        .eq("id", program_id)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Program not found")
    return {"data": response.data[0]}


@router.get("/grade-scale")
def list_grade_scale(db: APIDBManager = Depends(get_api_db)):
    response = db.client.table("grade_scale").select("*").execute()
    return {"data": response.data, "count": len(response.data)}


@router.get("/admission-deadlines")
def list_admission_deadlines(
    level: str | None = Query(default=None, description="Filter by level (undergraduate/graduate)"),
    semester: str | None = Query(default=None, description="Filter by semester"),
    db: APIDBManager = Depends(get_api_db),
):
    query = db.client.table("admission_deadlines").select("*")
    if level:
        query = query.ilike("level", f"%{level}%")
    if semester:
        query = query.ilike("semester", f"%{semester}%")
    response = query.execute()
    return {"data": response.data, "count": len(response.data)}


@router.get("/academic-calendar")
def list_academic_calendar(
    semester: str | None = Query(default=None, description="Filter by semester (e.g. Spring 2026)"),
    program_type: str | None = Query(default=None, description="Filter by program type"),
    calendar_type: str | None = Query(default=None, description="Filter by type: academic_calendar or exam_schedule"),
    db: APIDBManager = Depends(get_api_db),
):
    query = db.client.table("academic_calendar").select("*")
    if semester:
        query = query.ilike("semester", f"%{semester}%")
    if program_type:
        query = query.ilike("program_type", f"%{program_type}%")
    if calendar_type:
        query = query.eq("calendar_type", calendar_type)
    response = query.order("event_date").execute()
    return {"data": response.data, "count": len(response.data)}
