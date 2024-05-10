FROM python:3.12-bullseye

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
RUN rm requirements.txt

RUN mkdir -p /backup /config

COPY src /app
