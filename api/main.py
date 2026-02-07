import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from api.dependencies import get_api_db, APIDBManager
from api.routes import academic, people, campus, finance, info, search

app = FastAPI(
    title="EWU Database API",
    description="Read-only REST API for East West University data",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.API_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(academic.router)
app.include_router(people.router)
app.include_router(campus.router)
app.include_router(finance.router)
app.include_router(info.router)
app.include_router(search.router)


@app.get("/api/health", tags=["Meta"])
def health():
    return {"status": "healthy"}


@app.get("/api/last-update", tags=["Meta"])
def last_update(db: APIDBManager = Depends(get_api_db)):
    response = (
        db.client.table("scrape_metadata")
        .select("*")
        .order("last_run", desc=True)
        .limit(1)
        .execute()
    )
    if not response.data:
        return {"data": None}
    return {"data": response.data[0]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
