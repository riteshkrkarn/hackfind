from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, JobExecutionEvent
from apscheduler.schedulers.background import BackgroundScheduler

from app.agent.runner import run_agent_cycle
from app.config import get_settings

logger = logging.getLogger(__name__)
_scheduler: BackgroundScheduler | None = None

_last_run_at: datetime | None = None
_last_run_ok: bool | None = None
_last_run_error: str | None = None
_last_run_result: dict[str, Any] | None = None


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def run_tracked_agent_cycle() -> dict[str, Any]:
    """Wrapper so scheduler/manual runs share logging and last-run status."""
    global _last_run_at, _last_run_ok, _last_run_error, _last_run_result
    _last_run_at = _utc_now()
    try:
        result = run_agent_cycle()
        _last_run_ok = True
        _last_run_error = None
        _last_run_result = {
            "fetched": result.get("fetched"),
            "new": result.get("new"),
            "matched": result.get("matched"),
            "reminders": result.get("reminders"),
        }
        return result
    except Exception as exc:  # noqa: BLE001
        _last_run_ok = False
        _last_run_error = str(exc)
        _last_run_result = None
        logger.exception("Scheduled agent cycle failed")
        raise


def _on_job_event(event: JobExecutionEvent) -> None:
    if event.exception:
        logger.error(
            "APScheduler job %s raised: %s",
            event.job_id,
            event.exception,
            exc_info=event.exception,
        )
    else:
        logger.info("APScheduler job %s finished successfully", event.job_id)


def scheduler_status() -> dict[str, Any]:
    settings = get_settings()
    next_run: str | None = None
    running = bool(_scheduler and _scheduler.running)
    if _scheduler and _scheduler.running:
        job = _scheduler.get_job("hackfind-agent-cycle")
        if job and job.next_run_time:
            next_run = job.next_run_time.isoformat()

    return {
        "running": running,
        "interval_minutes": settings.agent_cron_minutes,
        "next_run_at": next_run,
        "last_run_at": _last_run_at.isoformat() if _last_run_at else None,
        "last_run_ok": _last_run_ok,
        "last_run_error": _last_run_error,
        "last_run_result": _last_run_result,
    }


def start_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler and _scheduler.running:
        return _scheduler

    settings = get_settings()
    minutes = max(1, settings.agent_cron_minutes)
    scheduler = BackgroundScheduler()
    scheduler.add_listener(_on_job_event, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    # Fire once at startup, then every N minutes. Without next_run_time=now,
    # APScheduler waits a full interval first — and uvicorn --reload resets
    # that timer on every code change, so the job never runs in development.
    scheduler.add_job(
        run_tracked_agent_cycle,
        trigger="interval",
        minutes=minutes,
        id="hackfind-agent-cycle",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=minutes * 60,
        next_run_time=_utc_now(),
    )
    scheduler.start()
    _scheduler = scheduler
    job = scheduler.get_job("hackfind-agent-cycle")
    logger.info(
        "Scheduler started: every %s minutes (next run %s)",
        minutes,
        job.next_run_time if job else "unknown",
    )
    return scheduler


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
    _scheduler = None
