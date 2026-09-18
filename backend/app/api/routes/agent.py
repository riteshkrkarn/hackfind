from typing import Any

from fastapi import APIRouter

from app.agent.scheduler import run_tracked_agent_cycle, scheduler_status

router = APIRouter(prefix="/agent", tags=["agent"])


@router.get("/status")
def agent_status() -> dict[str, Any]:
    return scheduler_status()


@router.post("/run")
def trigger_agent() -> dict[str, Any]:
    # Same wrapper as the cron job so last_run_* status stays in sync.
    return run_tracked_agent_cycle()
