FROM python:3.10-slim

RUN apt-get update \
    && apt-get install -y ffmpeg curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -U pip \
    && pip install --no-cache-dir -r requirements.txt

CMD bash start