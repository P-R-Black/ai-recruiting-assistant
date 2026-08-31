from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.jobs.router import router as jobs_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="AI Recruiting Assistant API",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs_router)


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "message": "AI Recruiting Assistant backend is running"
        }


@jobs_router.post
def create_new_job():
    pass

