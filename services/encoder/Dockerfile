FROM python:3.10-slim

WORKDIR /home

RUN apt-get update && \
    apt-get install git -y

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

COPY ./services/encoder/requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./common ./common
COPY ./services/encoder .

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--no-access-log", \
     "--host", "0.0.0.0", "--port", "8080"]