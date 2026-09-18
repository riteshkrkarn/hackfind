import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from app.agent.scheduler import start_scheduler, stop_scheduler
from app.api.router import api_router
from app.config import get_settings
from app.db.models import NotificationChannel
from app.db.session import engine, init_db
from app.notifications.dispatch import wire_notification_listeners

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


def ensure_default_console_channel() -> None:
    with Session(engine) as session:
        existing = session.exec(
            select(NotificationChannel).where(NotificationChannel.channel == "console")
        ).first()
        if existing:
            return
        session.add(
            NotificationChannel(
                channel="console",
                enabled=True,
                config={},
                reminder_thresholds_days=[7, 1, 0],
            )
        )
        session.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    ensure_default_console_channel()
    wire_notification_listeners()
    start_scheduler()
    logger.info("Hackfind backend ready")
    yield
    stop_scheduler()


settings = get_settings()
app = FastAPI(
    title="Hackfind API",
    version="0.1.0",
    description="Hackathon discovery agent, filters, deadlines, and notifications",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
