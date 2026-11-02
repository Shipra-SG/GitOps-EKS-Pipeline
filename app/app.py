import os
from flask import Flask, jsonify, request

app = Flask(__name__)

APP_VERSION = os.getenv("APP_VERSION", "v1")

tasks = [{"id": 1, "title": "Learn GitOps"}]


@app.route("/")
def home():
    return jsonify(message="Hello from GitOps project!", version=APP_VERSION)


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks)


@app.route("/api/tasks", methods=["POST"])
def add_task():
    data = request.get_json(silent=True)
    if not data or "title" not in data:
        return jsonify(error="title is required"), 400
    task = {"id": len(tasks) + 1, "title": data["title"]}
    tasks.append(task)
    return jsonify(task), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
