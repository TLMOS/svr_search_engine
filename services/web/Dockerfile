FROM python:3.10-slim

WORKDIR /home

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && apt-get install ffmpeg libsm6 libxext6  -y

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

COPY ./services/web/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install uwsgi

COPY ./common ./common
COPY ./services/web .

RUN groupadd -r app && \
    useradd -r -g app -d /home -s /sbin/nologin -c "Docker image user" app && \
    chown -R app:app /home

USER app

EXPOSE 8080

CMD ["uwsgi", "--ini", "uwsgi.ini", "--http", "0.0.0.0:8080"]