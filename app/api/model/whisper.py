import ffmpeg
from functools import lru_cache
import numpy as np

import whisper
from typing import Tuple
import jiwer
import json

SAMPLE_RATE = 16000


@lru_cache
def get_whisper_model():
    model = whisper.load_model("base")
    return model


def speech_to_text(audio_file, answer):
    # load audio and pad/trim it to fit 30 seconds
    model = get_whisper_model()

    audio = load_audio(audio_file)
    audio = whisper.pad_or_trim(audio)

    # # make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(audio).to(model.device)

    # # decode the audio
    options = whisper.DecodingOptions(language="Korean", fp16=False)
    result = whisper.decode(model, mel, options)
    prediction = result.text
    _cer = get_cer(answer, prediction)['cer']

    return prediction, _cer * 100


def load_audio(audio_file, sr: int = SAMPLE_RATE):
    """
    Modified from https://github.com/openai/whisper/blob/main/whisper/audio.py to accept a file object
    """

    try:
        # This launches a subprocess to decode audio while down-mixing and resampling as necessary.
        # Requires the ffmpeg CLI and `ffmpeg-python` package to be installed.
        out, _ = (
            ffmpeg.input("pipe:", threads=0)
            .output("-", format="s16le", acodec="pcm_s16le", ac=1, ar=sr)
            .run(cmd="ffmpeg", capture_stdout=True, capture_stderr=True, input=audio_file.file.read())
        )
    except ffmpeg.Error as e:
        raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e

    return np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0


def get_cer(reference, transcription, rm_punctuation = True) -> json:

    # 문자 오류율(CER)은 자동 음성 인식 시스템의 성능에 대한 일반적인 메트릭입니다.
    # CER은 WER(단어 오류율)과 유사하지만 단어 대신 문자에 대해 작동합니다.
    # 이 코드에서는 문제는 사람들이 띄어쓰기를 지키지 않고 작성한 텍스트를 컴퓨터가 정확하게 인식하는 것이 매우 어렵기 때문에 인식에러에서 생략합니다.
    # CER의 출력은 특히 삽입 수가 많은 경우 항상 0과 1 사이의 숫자가 아닙니다. 이 값은 종종 잘못 예측된 문자의 백분율과 연관됩니다. 값이 낮을수록 좋습니다.
    # CER이 0인 ASR 시스템의 성능은 완벽한 점수입니다.

    # CER = (S + D + I) / N = (S + D + I) / (S + D + C)
    # S is the number of the substitutions,
    # D is the number of the deletions,
    # I is the number of the insertions,
    # C is the number of the correct characters,
    # N is the number of the characters in the reference (N=S+D+C).

    refs = jiwer.RemoveWhiteSpace(replace_by_space=False)(reference)
    trans = jiwer.RemoveWhiteSpace(replace_by_space=False)(transcription)

    if rm_punctuation == True:
        refs = jiwer.RemovePunctuation()(refs)
        trans = jiwer.RemovePunctuation()(trans)
    else:
        refs = reference
        trans = transcription

    [hits, cer_s, cer_d, cer_i] = _measure_cer(refs, trans)

    substitutions = cer_s
    deletions = cer_d
    insertions = cer_i

    incorrect = substitutions + deletions + insertions
    total = substitutions + deletions + hits + insertions

    cer = incorrect / total

    result = {'cer' : cer, 'substitutions' : substitutions, 'deletions' : deletions, 'insertions': insertions }

    #return cer, substitutions, deletions, insertions
    return result


def levenshtein(u, v):
    prev = None
    curr = [0] + list(range(1, len(v) + 1))
    # Operations: (SUB, DEL, INS)
    prev_ops = None
    curr_ops = [(0, 0, i) for i in range(len(v) + 1)]
    for x in range(1, len(u) + 1):
        prev, curr = curr, [x] + ([None] * len(v))
        prev_ops, curr_ops = curr_ops, [(0, x, 0)] + ([None] * len(v))
        for y in range(1, len(v) + 1):
            delcost = prev[y] + 1
            addcost = curr[y - 1] + 1
            subcost = prev[y - 1] + int(u[x - 1] != v[y - 1])
            curr[y] = min(subcost, delcost, addcost)
            if curr[y] == subcost:
                (n_s, n_d, n_i) = prev_ops[y - 1]
                curr_ops[y] = (n_s + int(u[x - 1] != v[y - 1]), n_d, n_i)
            elif curr[y] == delcost:
                (n_s, n_d, n_i) = prev_ops[y]
                curr_ops[y] = (n_s, n_d + 1, n_i)
            else:
                (n_s, n_d, n_i) = curr_ops[y - 1]
                curr_ops[y] = (n_s, n_d, n_i + 1)
    return curr[len(v)], curr_ops[len(v)]


def _measure_cer(
        reference : str, transcription : str
) -> Tuple[int, int, int, int]:
    """
    소스 단어를 대상 단아로 변환하는 데 필요한 편집 작업(삭제, 삽입, 바꾸기)의 수를 확인합니다.
    hints 횟수는 소스 딘아의 전체 길이에서 삭제 및 대체 횟수를 빼서 제공할 수 있습니다.

    :param transcription: 대상 단어로 변환할 소스 문자열
    :param reference: 소스 단어
    :return: a tuple of #hits, #substitutions, #deletions, #insertions
    """

    ref, hyp = [], []

    ref.append(reference)
    hyp.append(transcription)

    cer_s, cer_i, cer_d, cer_n = 0, 0, 0, 0
    sen_err = 0

    for n in range(len(ref)):
        # update CER statistics
        _, (s, i, d) = levenshtein(hyp[n], ref[n])
        cer_s += s
        cer_i += i
        cer_d += d
        cer_n += len(ref[n])

        # update SER statistics
        if s + i + d > 0:
            sen_err += 1

    substitutions = cer_s
    deletions = cer_d
    insertions = cer_i
    hits = len(reference) - (substitutions + deletions) #correct characters

    return hits, substitutions, deletions, insertions
