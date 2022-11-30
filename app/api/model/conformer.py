import logging
import os

from functools import lru_cache
import nemo.collections.asr as nemo_asr

from .utils import get_cer


@lru_cache
def get_conformer_ctc():
    model = nemo_asr.models.ASRModel.restore_from("app/Conformer-CTC-BPE-8000-KOR.nemo")
    return model


def speech_to_text(audio_file, answer):
    model = get_conformer_ctc()
    path = f"app/temp/{audio_file.filename}"
    prediction = ""
    cer = 100

    with open(path, "wb") as f:
        f.write(audio_file.file.read())
    try:
        result = model.transcribe([path])
    except Exception as e:
        logging.error(f"에러 발생 [{e}]")
    else:
        prediction = result[0]
        cer = get_cer(answer, prediction)['cer']
    finally:
        os.remove(path)

    return prediction, cer * 100
