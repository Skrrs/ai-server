from fastapi import APIRouter

from .endpoints import voice


api_router = APIRouter()

api_router.include_router(voice.router, tags=["model"], prefix="/model")
