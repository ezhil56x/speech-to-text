FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg libsndfile1 && \
    pip install --no-cache-dir numpy

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "5005"]
