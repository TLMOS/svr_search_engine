FROM python:3.10-slim

RUN apt-get update && \
    apt-get install git -y

WORKDIR /home

COPY ./requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

RUN pip3 install git+https://github.com/openai/CLIP.git

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--no-access-log", \
     "--host", "0.0.0.0", "--port", "8000"]