from python:3.8

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

RUN apt-get update && apt-get install libgl1-mesa-glx -y

CMD python app.py