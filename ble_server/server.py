from flask import Flask, request, jsonify
import mysql.connector
from dotenv import load_dotenv
import os
import struct
import re

load_dotenv()
app = Flask(__name__)

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}
TABLE_NAME = os.getenv("TABLE_NAME")
if not TABLE_NAME or not re.fullmatch(r"[A-Za-z0-9_]+", TABLE_NAME):
    raise ValueError("Virheellinen TABLE_NAME .env-tiedostossa")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "server_running"}), 200


@app.route("/data", methods=["POST"])
def receive_data():

    data = request.get_json(silent=True)

    if not data or "data" not in data:
        return jsonify({"error": "Missing data"}), 400

    try:
        raw = bytes.fromhex(data["data"])
        if len(raw) != 8:
            return jsonify({
                "error": "Expected 8 bytes",
                "received": len(raw)
            }), 400

        values = struct.unpack("<4H", raw)

        sensor_a, sensor_b, sensor_c, sensor_d = values

        groupid = int(data.get("groupid", 0))
        from_mac = str(data.get("from_mac", "0"))
        to_mac = str(data.get("to_mac", "0"))

        if len(from_mac) > 32 or len(to_mac) > 32:
            return jsonify({"error": "MAC address too long"}), 400

        db = mysql.connector.connect(**DB_CONFIG)

        try:
            cursor = db.cursor()

            sql = f"""
                INSERT INTO `{TABLE_NAME}` (
                    groupid,
                    from_mac,
                    to_mac,
                    sensorvalue_a,
                    sensorvalue_b,
                    sensorvalue_c,
                    sensorvalue_d
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            cursor.execute(sql, (
                groupid,
                from_mac,
                to_mac,
                sensor_a,
                sensor_b,
                sensor_c,
                sensor_d
            ))

            db.commit()

            record_id = cursor.lastrowid
            cursor.close()

        finally:
            db.close()

        print(
            f"Tallennettu ID={record_id}, "
            f"data={values}, MAC={from_mac}"
        )

        return jsonify({
            "status": "OK",
            "id": record_id,
            "values": values
        }), 200

    except (ValueError, KeyError) as e:
        return jsonify({"error": str(e)}), 400

    except mysql.connector.Error as e:
        print("MySQL error:", e)
        return jsonify({"error": "Database error"}), 500

    except Exception as e:
        print("Server error:", e)
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
