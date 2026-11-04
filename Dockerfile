# ENSP461 Lab 2 - sample application image
FROM python:3.12-slim

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

EXPOSE 5000
ENV APP_VERSION=2.0.0

CMD ["python3", "app.py"]
