from flask import Flask, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def add(a, b):
    return a + b

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# ---------- BASIC ROUTES ----------

@app.route("/ping", methods=["GET"])
def ping():
    return "pong from Intelligent IoT Flask API in Docker"

@app.route("/")
def index():
    return "Mini API med MySQL kører. Prøv /api/devices"

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

# ---------- DEVICES API ----------

@app.route("/api/devices", methods=["GET"])
def get_devices():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, location, status, customer_name, last_seen FROM devices")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)

@app.route("/api/devices/<int:device_id>", methods=["GET"])
def get_device(device_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, name, location, status, customer_name, last_seen FROM devices WHERE id = %s",
        (device_id,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        return jsonify(row)
    else:
        return jsonify({"error": "Device not found"}), 404

@app.route("/api/devices", methods=["POST"])
def create_device():
    data = request.get_json()
    required_fields = ["name", "location", "status", "customer_name"]
    if not data or any(f not in data for f in required_fields):
        return jsonify({"error": f"Missing one of {required_fields}"}), 400
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO devices (name, location, status, customer_name, last_seen) VALUES (%s, %s, %s, %s, NOW())",
        (data["name"], data["location"], data["status"], data["customer_name"])
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"id": new_id, "name": data["name"], "location": data["location"], "status": data["status"], "customer_name": data["customer_name"]}), 201

@app.route("/api/devices/<int:device_id>", methods=["PUT"])
def update_device(device_id):
    data = request.get_json()
    required_fields = ["name", "location", "status", "customer_name"]
    if not data or any(f not in data for f in required_fields):
        return jsonify({"error": f"Missing one of {required_fields}"}), 400
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM devices WHERE id = %s", (device_id,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return jsonify({"error": "Device not found"}), 404
    cursor.execute(
        "UPDATE devices SET name = %s, location = %s, status = %s, customer_name = %s, last_seen = NOW() WHERE id = %s",
        (data["name"], data["location"], data["status"], data["customer_name"], device_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"id": device_id, "name": data["name"], "location": data["location"], "status": data["status"], "customer_name": data["customer_name"]})

@app.route("/api/devices/<int:device_id>", methods=["DELETE"])
def delete_device(device_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM devices WHERE id = %s", (device_id,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return jsonify({"error": "Device not found"}), 404
    cursor.execute("DELETE FROM devices WHERE id = %s", (device_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": f"Device {device_id} deleted"})

# ---------- PREDICTIVE MAINTENANCE ----------

THRESHOLD = 80.0

@app.route("/api/sensor-data", methods=["POST"])
def receive_sensor_data():
    data = request.get_json()
    required_fields = ["device_id", "sensor_type", "value"]
    if not data or any(f not in data for f in required_fields):
        return jsonify({"error": f"Missing one of {required_fields}"}), 400
    value = data["value"]
    unit = data.get("unit", "unknown")
    if value > THRESHOLD:
        status = "ALARM"
        message = f"Anomaly detected! {data['sensor_type']} value {value} exceeds threshold {THRESHOLD}"
    else:
        status = "OK"
        message = f"Sensor value {value} is within normal range"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sensor_events (device_id, sensor_type, value, unit, status, message, created_at) VALUES (%s, %s, %s, %s, %s, %s, NOW())",
        (data["device_id"], data["sensor_type"], value, unit, status, message)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"status": status, "message": message, "device_id": data["device_id"], "value": value, "threshold": THRESHOLD}), 201

@app.route("/api/sensor-events", methods=["GET"])
def get_sensor_events():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sensor_events ORDER BY created_at DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)

@app.route("/api/alarms", methods=["GET"])
def get_alarms():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM alarms WHERE resolved = FALSE ORDER BY created_at DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)

@app.route("/api/alarms", methods=["POST"])
def create_alarm():
    data = request.get_json()
    required_fields = ["device_id", "alarm_type", "severity", "message"]
    if not data or any(f not in data for f in required_fields):
        return jsonify({"error": f"Missing one of {required_fields}"}), 400
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO alarms (device_id, alarm_type, severity, message) VALUES (%s, %s, %s, %s)",
        (data["device_id"], data["alarm_type"], data["severity"], data["message"])
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({
        "id": new_id,
        "device_id": data["device_id"],
        "alarm_type": data["alarm_type"],
        "severity": data["severity"],
        "message": data["message"],
        "resolved": False
    }), 201

@app.route("/api/alarms/<int:alarm_id>/resolve", methods=["PUT"])
def resolve_alarm(alarm_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM alarms WHERE id = %s", (alarm_id,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return jsonify({"error": "Alarm not found"}), 404
    cursor.execute("UPDATE alarms SET resolved = TRUE WHERE id = %s", (alarm_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": f"Alarm {alarm_id} resolved"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)