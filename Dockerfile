FROM python:3.9-slim

LABEL org.opencontainers.image.source https://github.com/tbobm/payler

WORKDIR /app

COPY configuration.yml /

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN pip install .

ENTRYPOINT ["payler", "--config-file", "/configuration.yml"]
