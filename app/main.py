import logging

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.api import api_router


logging.basicConfig(level=logging.INFO)


def create_app():

    _app = FastAPI(title="Korean Speech Recognition API",
                   description="Whisper and Conformer-CTC",
                   version="1.0.0")
    _app.include_router(api_router, prefix="/api/ai")
    return _app


origins = [
    "http://18.178.180.144",
]

app = create_app()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)