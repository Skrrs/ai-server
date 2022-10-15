import os

from functools import lru_cache
import nemo.collections.asr as nemo_asr

from .utils import get_cer


@lru_cache
def get_conformer_ctc():
    model = nemo_asr.models.ASRModel.restore_from("Conformer-CTC-BPE-8000-KOR.nemo")
    return model


def speech_to_text(audio_file, answer):
    model = get_conformer_ctc()
    path = f"temp/{audio_file.filename}"
    with open(path, "wb") as f:
        f.write(audio_file.file.read())

    result = model.transcribe([path])
    os.remove(path)
    prediction = result[0]
    _cer = get_cer(answer, prediction)['cer']

    return prediction, _cer * 100
