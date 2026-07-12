from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db


app = FastAPI(
    title="AI Recruiting Assistant API",
    version="0.1.0"
)

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "message": "AI Recruiting Assistant backend is running"
        }