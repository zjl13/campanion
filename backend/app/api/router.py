from fastapi import APIRouter

from app.api.routes import auth, buddies, calendar, chat, goals, me, proofs, stats, tasks


api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(me.router)
api_router.include_router(buddies.router)
api_router.include_router(calendar.router)
api_router.include_router(goals.router)
api_router.include_router(tasks.router)
api_router.include_router(proofs.router)
api_router.include_router(chat.router)
api_router.include_router(stats.router)

