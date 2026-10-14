import pytest

@pytest.mark.asyncio
async def test_automl_select(client):
    j = await client.post("/api/jobs", json={"name": "churn", "dataset_uri": "file://x.csv"})
    jid = j.json()["id"]
    lb = await client.get(f"/api/jobs/{jid}/leaderboard")
    assert len(lb.json()["candidates"]) >= 2
    top = lb.json()["candidates"][0]["id"]
    s = await client.post(f"/api/candidates/{top}/select")
    assert s.json()["selected"] is True
