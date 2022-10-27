FROM python:3.9

WORKDIR /mask-ai

COPY ./requirements.txt /mask-ai/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /mask-ai/requirements.txt
RUN apt-get -y update
RUN apt-get install -y ffmpeg

COPY ./app /mask-ai/app

WORKDIR /mask-ai/app
RUN mkdir -p temp

WORKDIR /mask-ai

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5022"]
