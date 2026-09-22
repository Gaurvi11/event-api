import sqlite3
from flask import Flask, request, jsonify


app = Flask(__name__)


def init_db():
    conn = sqlite3.connect("events.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            value REAL NOT NULL,
            timestamp TEXT NOT NULL,
            source TEXT NOT NULL)
    """)
    conn.commit()
    conn.close()


@app.route("/hello", methods=["GET"])
def hello():
    return jsonify({"message": "hello World"})


@app.route("/events", methods=["POST"])
def create_event():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    required_fields = ["type", "value", "timestamp", "source"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400

    if not isinstance(data["value"], (int, float)):
        return jsonify({"error": "'value' must be a number"}), 400

    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()
    cursor.execute(
            "INSERT INTO events(type, value, timestamp, source) VALUES (?, ?, ?, ?)", (data["type"], data["value"], data["timestamp"], data["source"]))
    conn.commit()
    event_id = cursor.lastrowid
    conn.close()
    
    return jsonify({"id": event_id, "received": data}), 201

    


@app.route("/events", methods=["GET"])
def list_events():
    event_type = request.args.get("type")

    conn = sqlite3.connect("events.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if event_type:
        cursor.execute("SELECT * FROM events WHERE type = ?", (event_type,))
    else:
        cursor.execute("SELECT * FROM events")
    rows = cursor.fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])

@app.route("/events/summary", methods=["GET"])
def event_summary():
    start = request.args.get("start")
    end = request.args.get("end")

    conn = sqlite3.connect("events.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT type, COUNT(*) as count, AVG(value) as avg_value FROM events"
    params = []

    if start and end:
        query += " WHERE timestamp >= ? AND timestamp <= ?"
        params.extend([start, end])

    query += " GROUP BY type"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

    

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5001)
