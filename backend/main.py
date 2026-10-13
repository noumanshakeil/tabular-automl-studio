"""Tabular AutoML Studio — FastAPI backend + Jinja UI."""
from __future__ import annotations

import json
import uuid
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import settings
from .llm import complete

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / "data" / "store.json"
FIELDS = ['dataset', 'target', 'metric']

app = FastAPI(title="Tabular AutoML Studio", version="1.0.0")
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")
templates = Jinja2Templates(directory=str(ROOT / "templates"))


def load_store() -> dict:
    if not DATA.exists():
        DATA.parent.mkdir(parents=True, exist_ok=True)
        payload = {"runs": [
  {
    "id": "ar1",
    "dataset": "leads.csv",
    "target": "converted",
    "metric": "auc"
  }
]}
        DATA.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return json.loads(DATA.read_text(encoding="utf-8"))


def save_store(store: dict) -> None:
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(store, indent=2), encoding="utf-8")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "tabular-automl-studio", "llm_mode": settings.llm_mode}


@app.get("/api/runs")
def list_items() -> dict:
    store = load_store()
    return {"runs": store.get("runs", [])}


@app.post("/api/runs")
def create_item(payload: dict) -> dict:
    store = load_store()
    item = {"id": uuid.uuid4().hex[:8]}
    for key in FIELDS:
        item[key] = payload.get(key)
    store.setdefault("runs", []).insert(0, item)
    save_store(store)
    return item


@app.post("/api/train_baseline")
def run_action(payload: dict) -> dict:
    """Train a mock baseline and return metrics."""
    prompt = (
        "You are the AI engine for Tabular AutoML Studio.\n"
        "Task: Train a mock baseline and return metrics.\n"
        f"Input JSON: {json.dumps(payload)[:4000]}"
    )
    text = complete(prompt)
    return {"ok": True, "action": "train_baseline", "result": text, "mode": settings.llm_mode}


@app.get("/", response_class=HTMLResponse)
def home(request: Request, last_result: str | None = None) -> HTMLResponse:
    store = load_store()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Tabular AutoML Studio",
            "description": "Tabular AutoML studio for train/compare baselines with leaderboard UI.",
            "resource": "runs",
            "action": "train_baseline",
            "action_desc": "Train a mock baseline and return metrics",
            "items": store.get("runs", []),
            "llm_mode": settings.llm_mode,
            "last_result": last_result,
        },
    )


@app.post("/ui/create", response_class=HTMLResponse)
async def ui_create(request: Request) -> HTMLResponse:
    form = await request.form()
    data = {k: form.get(k) for k in FIELDS}
    create_item(data)
    return home(request)


@app.post("/ui/action", response_class=HTMLResponse)
async def ui_action(request: Request, prompt: str = Form("demo")) -> HTMLResponse:
    result = run_action({"prompt": prompt})
    store = load_store()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Tabular AutoML Studio",
            "description": "Tabular AutoML studio for train/compare baselines with leaderboard UI.",
            "resource": "runs",
            "action": "train_baseline",
            "action_desc": "Train a mock baseline and return metrics",
            "items": store.get("runs", []),
            "llm_mode": settings.llm_mode,
            "last_result": result.get("result"),
        },
    )
