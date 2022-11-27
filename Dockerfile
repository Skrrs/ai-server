FROM python:3.9

WORKDIR /mask-ai

COPY ./requirements.txt /mask-ai/requirements.txt

RUN apt-get -y update && apt-get install -y cmake
RUN apt-get install -y ffmpeg

RUN pip install Cython
RUN pip install --no-cache-dir --upgrade -r /mask-ai/requirements.txt

COPY ./app /mask-ai/app

WORKDIR /mask-ai/app
RUN mkdir -p temp

WORKDIR /mask-ai

CMD ["gunicorn", "app.main:app", "--bind", "0.0.0.0:5022","--workers", "3","--worker-class", "uvicorn.workers.UvicornWorker"]
