from flask import Flask, jsonify
import os
import datetime

app = Flask(__name__)

APP_VERSION = os.environ.get("APP_VERSION", "1.0.0")


@app.route("/")
def index():
    return jsonify(
        {
            "message": "Hello from the CI/CD demo app!",
            "version": APP_VERSION,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
    )


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/add/<a>/<b>")
def add(a, b):
    try:
        a_int, b_int = int(a), int(b)
    except ValueError:
        return jsonify({"error": "a and b must be integers"}), 400
    return jsonify({"a": a_int, "b": b_int, "sum": a_int + b_int})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
