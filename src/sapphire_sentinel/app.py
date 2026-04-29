"""Flask demo for Sapphire Sentinel."""

from __future__ import annotations

import os

from flask import Flask, jsonify, render_template, request

from sapphire_sentinel.sentinel import build_demo_state, evaluate_from_payload

app = Flask(__name__, template_folder="../../templates")


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/demo")
def api_demo():
    return jsonify(build_demo_state())


@app.post("/api/evaluate")
def api_evaluate():
    payload = request.get_json(silent=True) or {}
    return jsonify(
        {
            "execution_enabled": False,
            "mode": "policy_preview_only",
            "decision": evaluate_from_payload(payload),
        }
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8097"))
    app.run(host="127.0.0.1", port=port, debug=False)

