import logging

import uvicorn

from fastapi import FastAPI

from core.config import conf
from api.api import api_router


logging.basicConfig(level=logging.INFO)


def create_app():

    _app = FastAPI()
    _app.include_router(api_router, prefix="/mask/ai")
    return _app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=conf().PORT, reload=conf().PROJ_RELOAD)
