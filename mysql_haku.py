import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import csv
from statistics import mean

load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
GROUP_ID = os.getenv("GROUP_ID")
CSV_FILE = "mittaukset_mysql.csv"

def hae_data():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
        )
        if conn.is_connected():
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT
                    timestamp,
                    groupid,
                    from_mac,
                    to_mac,
                    sensorvalue_a,
                    sensorvalue_b,
                    sensorvalue_c,
                    sensorvalue_d,
                    sensorvalue_e,
                    sensorvalue_f
                FROM rawdata
                WHERE groupid = %s
                ORDER BY timestamp DESC
            """
            cursor.execute(sql, (int(GROUP_ID),))
            data = cursor.fetchall()
            cursor.close()
            conn.close()
            return data
    except Error as e:
        print("MySQL-virhe:", e)
        return None

def kasittele_data(data):
    for row in data:
        sensorit = []
        for kirjain in "abcdef":
            arvo = row["sensorvalue_" + kirjain]
            if arvo is not None:
                try:
                    sensorit.append(float(arvo))
                except (ValueError, TypeError):
                    pass
    return data

def tallenna_csv(data):
    print("Tallennetaan CSV-tiedostoa")
    kentat = [
        "timestamp",
        "groupid",
        "from_mac",
        "to_mac",
        "sensorvalue_a",
        "sensorvalue_b",
        "sensorvalue_c",
        "sensorvalue_d",
        "sensorvalue_e",
        "sensorvalue_f",
    ]
    with open(CSV_FILE,"w",newline="",encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file,fieldnames=kentat,delimiter=";")
        writer.writeheader()
        writer.writerows(data)
    print("CSV tallennettu:", CSV_FILE)

def main():
    data = hae_data()
    if data is None:
        return
    data = kasittele_data(data)
    tallenna_csv(data)

if __name__ == "__main__":
    main()
