from __future__ import annotations
import json
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models import AutoMLJob, CandidateModel

async def create_job(session: AsyncSession, name: str, dataset_uri: str = "") -> AutoMLJob:
    job = AutoMLJob(
        id=uuid.uuid4().hex[:10],
        name=name.strip()[:120],
        dataset_uri=dataset_uri.strip()[:300],
        status="running",
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)
    return job

async def list_jobs(session: AsyncSession) -> list[AutoMLJob]:
    return list((await session.execute(select(AutoMLJob).order_by(AutoMLJob.created_at.desc()))).scalars())

async def seed_candidates(session: AsyncSession, job_id: str) -> list[CandidateModel]:
    specs = [
        ("logreg", 0.81, 0.77, {"C": 1.0}),
        ("xgboost", 0.86, 0.83, {"max_depth": 4}),
        ("rf", 0.84, 0.80, {"n_estimators": 120}),
    ]
    out: list[CandidateModel] = []
    for nm, acc, f1, params in specs:
        row = CandidateModel(
            id=uuid.uuid4().hex[:10],
            job_id=job_id,
            name=nm,
            accuracy=acc,
            f1=f1,
            params_json=json.dumps(params),
        )
        session.add(row)
        out.append(row)
    job = await session.get(AutoMLJob, job_id)
    if job:
        job.status = "complete"
    await session.commit()
    return out

async def leaderboard(session: AsyncSession, job_id: str) -> list[CandidateModel]:
    rows = list(
        (
            await session.execute(
                select(CandidateModel).where(CandidateModel.job_id == job_id).order_by(CandidateModel.f1.desc())
            )
        ).scalars()
    )
    return rows

async def select_winner(session: AsyncSession, candidate_id: str) -> CandidateModel:
    row = await session.get(CandidateModel, candidate_id)
    if not row:
        raise ValueError("not found")
    others = list(
        (
            await session.execute(select(CandidateModel).where(CandidateModel.job_id == row.job_id))
        ).scalars()
    )
    for c in others:
        c.selected = c.id == candidate_id
    await session.commit()
    await session.refresh(row)
    return row
