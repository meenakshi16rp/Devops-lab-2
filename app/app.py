"""Sample Flask application for ENSP461 Lab 2 - Containerization & Kubernetes."""
import os
import socket

from flask import Flask, jsonify

app = Flask(__name__)

VERSION = os.environ.get("APP_VERSION", "2.0.0")
GREETING = os.environ.get("GREETING", "Hello from Meenakshi Container Lab")
REDIS_HOST = os.environ.get("REDIS_HOST")


@app.route("/")
def index():
    visits = 0
    if REDIS_HOST:
        try:
            import redis
            visits = redis.Redis(host=REDIS_HOST, port=6379).incr("visits")
        except Exception as exc:
            visits = "redis unavailable: %s" % exc
    return jsonify(message=GREETING, version=VERSION,
                   hostname=socket.gethostname(), visits=visits)


@app.route("/health")
def health():
    return jsonify(status="UP"), 200


@app.route("/info")
def info():
    return jsonify(app="ensp461-lab2-sample-app", author="Meenakshi",
                   version=VERSION, container=socket.gethostname())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
