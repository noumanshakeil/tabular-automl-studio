from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import automl as svc

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, job_id: str | None = None, db: AsyncSession = Depends(get_db)):
    jobs = await svc.list_jobs(db)
    jid = job_id or (jobs[0].id if jobs else None)
    board = await svc.leaderboard(db, jid) if jid else []
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Tabular AutoML Studio", "jobs": jobs, "job_id": jid, "board": board},
    )

@router.post("/ui/jobs")
async def ui_job(name: str = Form(...), dataset_uri: str = Form("file://data/train.csv"), db: AsyncSession = Depends(get_db)):
    j = await svc.create_job(db, name, dataset_uri)
    await svc.seed_candidates(db, j.id)
    return RedirectResponse(f"/?job_id={j.id}", status_code=303)

@router.post("/ui/select")
async def ui_select(candidate_id: str = Form(...), job_id: str = Form(...), db: AsyncSession = Depends(get_db)):
    await svc.select_winner(db, candidate_id)
    return RedirectResponse(f"/?job_id={job_id}", status_code=303)
