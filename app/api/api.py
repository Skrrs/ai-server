from fastapi import APIRouter

from .endpoints import greeting


api_router = APIRouter()

api_router.include_router(greeting.router, tags=["greeting"], prefix="/greeting")
