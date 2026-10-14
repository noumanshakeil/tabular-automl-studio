from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import automl as svc

class JobIn(BaseModel):
    name: str = Field(min_length=2)
    dataset_uri: str = "file://data/train.csv"

router = APIRouter()

@router.get("/jobs")
async def jobs(db: AsyncSession = Depends(get_db)):
    rows = await svc.list_jobs(db)
    return {"jobs": [{"id": j.id, "name": j.name, "status": j.status} for j in rows]}

@router.post("/jobs")
async def create(payload: JobIn, db: AsyncSession = Depends(get_db)):
    j = await svc.create_job(db, payload.name, payload.dataset_uri)
    await svc.seed_candidates(db, j.id)
    return {"id": j.id, "status": "complete"}

@router.get("/jobs/{job_id}/leaderboard")
async def board(job_id: str, db: AsyncSession = Depends(get_db)):
    rows = await svc.leaderboard(db, job_id)
    return {
        "candidates": [
            {
                "id": c.id,
                "name": c.name,
                "accuracy": c.accuracy,
                "f1": c.f1,
                "selected": c.selected,
            }
            for c in rows
        ]
    }

@router.post("/candidates/{candidate_id}/select")
async def select(candidate_id: str, db: AsyncSession = Depends(get_db)):
    try:
        c = await svc.select_winner(db, candidate_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    return {"id": c.id, "selected": c.selected, "name": c.name}
