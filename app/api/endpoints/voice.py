import logging
import os
import sys
import json

from fastapi import APIRouter, Response, UploadFile, Form, File
from fastapi.responses import FileResponse

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from model import whisper, conformer

logging.basicConfig(level=logging.INFO)
router = APIRouter()


@router.post("/whisper")
def _whisper(audio_file: UploadFile = File(), answer: str = Form()):
    recognized_text, cer = whisper.speech_to_text(audio_file, answer)
    print(recognized_text, cer)
    output = {"recognized_text": recognized_text, "cer": cer}
    return Response(content=json.dumps(output), media_type="application/json")


@router.post("/conformer")
def _conformer(audio_file: UploadFile = File(), answer: str = Form()):
    recognized_text, cer = conformer.speech_to_text(audio_file, answer)
    print(recognized_text, cer)
    output = {"recognized_text": recognized_text, "cer": cer}
    return Response(content=json.dumps(output), media_type="application/json")
