# ai-server
AI server of MASK

Korean Speech Recognition API using Conformer-CTC and Whisper


## How to install
1. pip install virtualenv
2. virtualenv {venv_name}
3. source {venv_name}/bin/activate
4. pip install -r requirements.txt

## How to run
To run this code, you need ffmpeg.exe and .nemo file.

Those files are not in this repository due to the insufficient capacity.

If you need those files, contact 9997ijh@gmail.com

1. docker build -t {image_name} .
2. docker run -p {your host port}:5022 {image_name}

- Swagger
    ![img.png](resource/swagger.png)

- Using Postman
  - Conformer-CTC
    ![img_4.png](resource/conformer-ctc.png)
  - Whisper
    ![img_2.png](resource/whisper.png)


## Reference
- https://github.com/openai/whisper
- https://ffmpeg.org/
- https://github.com/kkroening/ffmpeg-python
- https://koreascience.kr/article/JAKO202128837810056.pdf

If you want ipynb version of the model, visit these repositories. 

- [conformer-ctc](https://github.com/Skrrs/ml_conformer_ctc)
- [whisper](https://github.com/Skrrs/ml_whisper)