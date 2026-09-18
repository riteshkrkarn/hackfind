from fastapi import APIRouter

from app.api.routes import agent, deadlines, filters, hackathons, notifications, sources

api_router = APIRouter()
api_router.include_router(hackathons.router)
api_router.include_router(filters.router)
api_router.include_router(notifications.router)
api_router.include_router(sources.router)
api_router.include_router(agent.router)
api_router.include_router(deadlines.router)
