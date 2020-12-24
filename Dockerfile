FROM python:3.8-slim

WORKDIR /app

COPY configuration.yml /

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN pip install .

ENTRYPOINT ["payler", "--config-file", "/configuration.yml"]
