# ENSP461 Lab 2 - container image for the sample Flask app
FROM python:3.12-slim

ARG APP_VERSION=2.0.0
ENV APP_VERSION=${APP_VERSION}

WORKDIR /app

# install dependencies first so this layer is cached
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy application code
COPY app/ .

EXPOSE 5000

# run as a non-root user
RUN useradd -m appuser
USER appuser

CMD ["python3", "app.py"]
