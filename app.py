from __future__ import annotations

from datetime import datetime
import os
import random
from uuid import uuid4

from flask import Flask, jsonify, render_template, request, url_for

app = Flask(__name__)


MANAGERS: dict[str, dict] = {}
TRANSACTIONS: dict[str, dict] = {}


YESTERDAY_ORDER = [
    {"sku": "buffalo milk 500ml", "product": "buffalo milk 500ml", "ordered_qty": 24},
    {"sku": "cow milk 500ml", "product": "cow milk 500ml", "ordered_qty": 18},
    {"sku": "curd pouch 480g", "product": "curd pouch 480g", "ordered_qty": 16},
    {"sku": "buffalo curd 400g", "product": "buffalo curd 400g", "ordered_qty": 14},
    {"sku": "paneer 200g", "product": "paneer 200g", "ordered_qty": 12},
]


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:8]}"


def _new_tx_id() -> str:
    for _ in range(30):
        tx_id = f"{random.randint(0, 99999):05d}"
        if tx_id not in TRANSACTIONS:
            return tx_id
    return f"{random.randint(0, 99999):05d}"


@app.route("/")
def launcher():
    return render_template("index.html")


@app.route("/manager/<manager_id>")
def manager_page(manager_id: str):
    return render_template("manager.html", manager_id=manager_id)


@app.route("/join/<tx_id>")
def join_page(tx_id: str):
    return render_template("join.html", tx_id=tx_id)


@app.route("/cfa/<tx_id>")
def cfa_page(tx_id: str):
    return render_template("cfa.html", tx_id=tx_id)


@app.route("/cfa-entry")
def cfa_entry_page():
    return render_template("cfa_entry.html")


@app.route("/manager-tx/<tx_id>")
def manager_tx_page(tx_id: str):
    return render_template("manager_tx.html", tx_id=tx_id)


@app.route("/manager-qr/<tx_id>")
def manager_qr_page(tx_id: str):
    return render_template("manager_qr.html", tx_id=tx_id)


@app.post("/api/managers")
def create_manager():
    manager_id = _new_id("mgr")
    MANAGERS[manager_id] = {
        "manager_id": manager_id,
        "created_at": _now_iso(),
        "transactions": [],
    }
    return jsonify({"manager_id": manager_id})


@app.get("/api/managers/<manager_id>")
def get_manager(manager_id: str):
    manager = MANAGERS.get(manager_id)
    if not manager:
        return jsonify({"error": "Manager session not found"}), 404

    manager_transactions = [
        TRANSACTIONS[tx_id]
        for tx_id in manager["transactions"]
        if tx_id in TRANSACTIONS
    ]
    manager_transactions.sort(key=lambda tx: tx["updated_at"], reverse=True)

    return jsonify(
        {
            "manager": manager,
            "transactions": manager_transactions,
        }
    )


@app.get("/api/managers/<manager_id>/yesterday-order")
def get_yesterday_order(manager_id: str):
    if manager_id not in MANAGERS:
        return jsonify({"error": "Manager session not found"}), 404

    items = [
        {
            "sku": item["sku"],
            "product": item["product"],
            "ordered_qty": item["ordered_qty"],
            "received_qty": item["ordered_qty"],
            "confirmed": False,
            "image_name": "",
        }
        for item in YESTERDAY_ORDER
    ]

    return jsonify({"items": items})


@app.post("/api/transactions")
def create_transaction():
    payload = request.get_json(silent=True) or {}

    manager_id = payload.get("manager_id")
    note_type = payload.get("note_type")
    items = payload.get("items", [])

    if manager_id not in MANAGERS:
        return jsonify({"error": "Manager session not found"}), 404

    if note_type not in {"GRN", "PRN"}:
        return jsonify({"error": "Invalid note type"}), 400

    if not items:
        return jsonify({"error": "At least one row is required"}), 400

    tx_id = _new_tx_id()
    tx = {
        "tx_id": tx_id,
        "manager_id": manager_id,
        "note_type": note_type,
        "items": items,
        "status": "draft",
        "version": 1,
        "cfa_note": "",
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    }

    TRANSACTIONS[tx_id] = tx
    MANAGERS[manager_id]["transactions"].append(tx_id)

    return jsonify(tx)


@app.get("/api/transactions/<tx_id>")
def get_transaction(tx_id: str):
    tx = TRANSACTIONS.get(tx_id)
    if not tx:
        return jsonify({"error": "Transaction not found"}), 404
    return jsonify(tx)


@app.put("/api/transactions/<tx_id>")
def update_transaction(tx_id: str):
    tx = TRANSACTIONS.get(tx_id)
    if not tx:
        return jsonify({"error": "Transaction not found"}), 404

    payload = request.get_json(silent=True) or {}
    items = payload.get("items")
    if not isinstance(items, list) or not items:
        return jsonify({"error": "Rows are required"}), 400

    tx["items"] = items
    tx["status"] = "draft"
    tx["version"] += 1
    tx["updated_at"] = _now_iso()
    tx["cfa_note"] = ""

    return jsonify(tx)


@app.post("/api/transactions/<tx_id>/generate-qr")
def generate_qr(tx_id: str):
    tx = TRANSACTIONS.get(tx_id)
    if not tx:
        return jsonify({"error": "Transaction not found"}), 404

    tx["status"] = "qr_generated"
    tx["updated_at"] = _now_iso()

    join_url = url_for("join_page", tx_id=tx_id, _external=True)
    return jsonify({"tx_id": tx_id, "join_url": join_url, "status": tx["status"]})


@app.post("/api/transactions/<tx_id>/cfa-decision")
def cfa_decision(tx_id: str):
    tx = TRANSACTIONS.get(tx_id)
    if not tx:
        return jsonify({"error": "Transaction not found"}), 404

    payload = request.get_json(silent=True) or {}
    decision = payload.get("decision")
    note = payload.get("note", "")

    if decision not in {"accept", "dispute"}:
        return jsonify({"error": "Invalid decision"}), 400

    if decision == "accept":
        tx["status"] = "completed"
    else:
        tx["status"] = "disputed"

    tx["cfa_note"] = note
    tx["updated_at"] = _now_iso()

    return jsonify(tx)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(debug=False, host="0.0.0.0", port=port)
