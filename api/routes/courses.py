from fastapi import APIRouter, Depends, HTTPException, Query

from api.dependencies import verify_api_key, get_api_db, APIDBManager

router = APIRouter(prefix="/api", tags=["Courses"], dependencies=[Depends(verify_api_key)])


@router.get("/courses/programs")
def list_course_programs(
    level: str | None = Query(default=None, description="Filter by level: undergraduate or graduate"),
    search: str | None = Query(default=None, description="Search by program name"),
    db: APIDBManager = Depends(get_api_db),
):
    query = db.client.table("course_programs").select(
        "id,program_code,program_name,level,total_credits,department,created_at,updated_at"
    )
    if level:
        query = query.eq("level", level.lower())
    if search:
        query = query.ilike("program_name", f"%{search}%")
    response = query.order("level").order("program_code").execute()
    return {"data": response.data, "count": len(response.data)}


@router.get("/courses/programs/{program_code}")
def get_course_program(
    program_code: str,
    db: APIDBManager = Depends(get_api_db),
):
    prog_resp = (
        db.client.table("course_programs")
        .select("*")
        .eq("program_code", program_code.lower())
        .execute()
    )
    if not prog_resp.data:
        raise HTTPException(status_code=404, detail="Program not found")
    program = prog_resp.data[0]

    courses_resp = (
        db.client.table("course_offerings")
        .select("*")
        .eq("program_code", program_code.lower())
        .order("section")
        .order("course_code")
        .execute()
    )

    grouped: dict[str, list] = {}
    for course in courses_resp.data:
        section = course.get("section") or "general"
        grouped.setdefault(section, []).append(course)

    program["courses"] = grouped
    return {"data": program}


@router.get("/courses")
def list_course_offerings(
    level: str | None = Query(default=None, description="Filter by level: undergraduate or graduate"),
    program: str | None = Query(default=None, description="Filter by program_code"),
    course_type: str | None = Query(default=None, description="Filter by course_type (Core, Elective, etc.)"),
    section: str | None = Query(default=None, description="Filter by section name"),
    search: str | None = Query(default=None, description="Search by course title or code"),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: APIDBManager = Depends(get_api_db),
):
    query = db.client.table("course_offerings").select("*")
    if level:
        query = query.eq("level", level.lower())
    if program:
        query = query.eq("program_code", program.lower())
    if course_type:
        query = query.ilike("course_type", f"%{course_type}%")
    if section:
        query = query.ilike("section", f"%{section}%")
    if search:
        query = query.or_(f"course_title.ilike.%{search}%,course_code.ilike.%{search}%")
    query = query.range(offset, offset + limit - 1).order("program_code").order("course_code")
    response = query.execute()
    return {"data": response.data, "count": len(response.data)}


@router.get("/courses/{course_code}")
def get_course_offering(
    course_code: str,
    program: str | None = Query(default=None, description="Program code for disambiguation"),
    db: APIDBManager = Depends(get_api_db),
):
    query = db.client.table("course_offerings").select("*").eq("course_code", course_code)
    if program:
        query = query.eq("program_code", program.lower())
    response = query.execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Course not found")
    if len(response.data) == 1:
        return {"data": response.data[0]}
    return {"data": response.data}
