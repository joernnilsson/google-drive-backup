FROM python:3.12-bullseye

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
RUN rm requirements.txt

RUN mkdir -p /backup /config

COPY src /app
WORKDIR /app

CMD ["/usr/local/bin/python3", "main.py", "--config-file", "/config/config.yaml", "--google-drive-credentials-file", "/config/service_account.json", "--schedule", "--run-now"]