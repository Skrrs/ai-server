import logging
import os

from fastapi import APIRouter, Response, UploadFile, Form, File
from fastapi.responses import FileResponse

logging.basicConfig(level=logging.INFO)
router = APIRouter()


@router.post("/", response_class=FileResponse)
async def greeting(audio_file: UploadFile = File(), answer: str = Form()):
    UPLOAD_DIRECTORY = "./"

    contents = await audio_file.read()
    with open(os.path.join(UPLOAD_DIRECTORY, audio_file.filename), "wb") as fp:
        fp.write(contents)

    recognized_text = audio_file.filename
    print(answer)

    return Response(content=recognized_text, media_type="application/json")
