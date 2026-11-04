import os
import socket
import time

from flask import Flask, jsonify, request
from markupsafe import escape

app = Flask(__name__)

APP_VERSION = os.getenv("APP_VERSION", "v1")
POD_NAME = os.getenv("HOSTNAME", socket.gethostname())
START_TIME = time.time()

tasks = [{"id": 1, "title": "Learn GitOps"}]

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GitOps on EKS</title>
<style>
:root { --h: __HUE__; }
* { box-sizing: border-box; }
body {
  margin: 0; min-height: 100vh; padding: 24px;
  display: flex; align-items: center; justify-content: center;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  color: #e8ecf4;
  background:
    radial-gradient(circle at 15% 10%, hsl(var(--h) 60% 24%), transparent 55%),
    radial-gradient(circle at 85% 90%, hsl(calc(var(--h) + 60) 60% 20%), transparent 55%),
    #0b1020;
  transition: background 0.6s;
}
.wrap { max-width: 860px; width: 100%; }
h1 { font-size: clamp(28px, 5vw, 44px); margin: 0 0 6px; }
.sub { opacity: 0.75; margin: 0 0 22px; }
.badge {
  display: inline-block; padding: 8px 18px; border-radius: 999px;
  background: hsl(var(--h) 70% 48%); color: #fff;
  font-weight: 700; letter-spacing: 1px; transition: background 0.6s;
}
.grid {
  display: grid; gap: 16px; margin: 24px 0;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}
.card {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px; padding: 18px 20px;
}
.label { font-size: 12px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.6; }
.value { font-size: 20px; font-weight: 600; margin-top: 6px; word-break: break-all; }
.dot {
  display: inline-block; width: 10px; height: 10px; margin-right: 8px;
  border-radius: 50%; background: #3ddc84; box-shadow: 0 0 10px #3ddc84;
}
.dot.bad { background: #ff5c5c; box-shadow: 0 0 10px #ff5c5c; }
.flow { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin-top: 10px; }
.step { padding: 10px 14px; border-radius: 12px; background: rgba(255, 255, 255, 0.08); font-size: 14px; }
.arrow { opacity: 0.5; }
footer { margin-top: 26px; opacity: 0.55; font-size: 13px; }
</style>
</head>
<body>
<div class="wrap">
  <h1>&#128640; GitOps on Amazon EKS</h1>
  <p class="sub">Push to Git, CI builds the image, ArgoCD syncs, Kubernetes runs it.</p>
  <span class="badge" id="badge">VERSION __VERSION__</span>

  <div class="grid">
    <div class="card">
      <div class="label">Status</div>
      <div class="value"><span id="dot" class="dot"></span><span id="status">checking...</span></div>
    </div>
    <div class="card">
      <div class="label">Served by pod</div>
      <div class="value" id="pod">-</div>
    </div>
    <div class="card">
      <div class="label">Pod uptime</div>
      <div class="value" id="uptime">-</div>
    </div>
  </div>

  <div class="card">
    <div class="label">Delivery pipeline</div>
    <div class="flow">
      <span class="step">&#128221; Git push</span><span class="arrow">&#10140;</span>
      <span class="step">&#9881;&#65039; GitHub Actions</span><span class="arrow">&#10140;</span>
      <span class="step">&#128230; Amazon ECR</span><span class="arrow">&#10140;</span>
      <span class="step">&#128260; ArgoCD</span><span class="arrow">&#10140;</span>
      <span class="step">&#9096;&#65039; Amazon EKS</span>
    </div>
  </div>

  <footer>Built by Shipra &middot; Cloud With Shipra &middot; refreshes every 3 seconds</footer>
</div>

<script>
function hue(v) {
  var s = 0;
  for (var i = 0; i < v.length; i++) { s += v.charCodeAt(i); }
  return (s * 97) % 360;
}
function fmt(s) {
  var m = Math.floor(s / 60), h = Math.floor(m / 60);
  if (h > 0) { return h + "h " + (m % 60) + "m"; }
  if (m > 0) { return m + "m " + (s % 60) + "s"; }
  return s + "s";
}
function refresh() {
  fetch("/api/info", { cache: "no-store" })
    .then(function (r) { return r.json(); })
    .then(function (d) {
      document.getElementById("pod").textContent = d.pod;
      document.getElementById("uptime").textContent = fmt(d.uptime_seconds);
      document.getElementById("badge").textContent = "VERSION " + d.version;
      document.documentElement.style.setProperty("--h", hue(d.version));
      document.getElementById("status").textContent = "Healthy";
      document.getElementById("dot").className = "dot";
    })
    .catch(function () {
      document.getElementById("status").textContent = "Unreachable";
      document.getElementById("dot").className = "dot bad";
    });
}
refresh();
setInterval(refresh, 3000);
</script>
</body>
</html>
"""


def version_hue(version):
    return sum(ord(c) for c in version) * 97 % 360


@app.route("/")
def home():
    return PAGE.replace("__VERSION__", str(escape(APP_VERSION))).replace(
        "__HUE__", str(version_hue(APP_VERSION))
    )


@app.route("/api/info")
def info():
    return jsonify(
        version=APP_VERSION,
        pod=POD_NAME,
        uptime_seconds=int(time.time() - START_TIME),
    )


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
