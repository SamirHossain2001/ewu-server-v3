from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import verify_api_key, get_api_db, APIDBManager

router = APIRouter(prefix="/api", tags=["Information"], dependencies=[Depends(verify_api_key)])


@router.get("/documents")
def list_documents(db: APIDBManager = Depends(get_api_db)):
    response = (
        db.client.table("university_documents")
        .select("slug, title, source_file")
        .execute()
    )
    return {"data": response.data, "count": len(response.data)}


@router.get("/documents/{slug}")
def get_document(slug: str, db: APIDBManager = Depends(get_api_db)):
    response = (
        db.client.table("university_documents")
        .select("*")
        .eq("slug", slug)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"data": response.data[0]}


@router.get("/policies")
def list_policies(db: APIDBManager = Depends(get_api_db)):
    response = db.client.table("policies").select("*").execute()
    return {"data": response.data, "count": len(response.data)}


@router.get("/newsletters")
def list_newsletters(db: APIDBManager = Depends(get_api_db)):
    response = (
        db.client.table("newsletters")
        .select("*")
        .order("year", desc=True)
        .execute()
    )
    return {"data": response.data, "count": len(response.data)}


@router.get("/partnerships")
def list_partnerships(db: APIDBManager = Depends(get_api_db)):
    response = db.client.table("partnerships").select("*").execute()
    return {"data": response.data, "count": len(response.data)}
