import requests
import csv
from statistics import mean

URL = "http://172.20.241.118/csv.php"
CSV_FILE = "mittaukset.csv"

def hae_data():
    try:
        response = requests.get(URL, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print("yhteysvirhe:", e)
        return None
    except ValueError:
        print("Palvelin ei palauttanut kelvollista JSON-dataa.")
        return None

def kasittele_data(data):
    for row in data:
        sensorit = []
        for kirjain in "abcdef":
            arvo = row.get("sensorvalue_" + kirjain)
            if arvo is not None and arvo != "":
                try:
                    sensorit.append(float(arvo))
                except (ValueError, TypeError):
                    pass
    return data

def tallenna_csv(data):
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
    with open(CSV_FILE, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file,fieldnames=kentat,delimiter=";")
        writer.writeheader()
        writer.writerows(data)
    print("CSV-tiedosto tallennettu:", CSV_FILE)

def main():
    data = hae_data()
    if data is None:
        return
    if isinstance(data, dict):
        print("Palvelimen virheilmoitus:", data.get("error"))
        return
    data = kasittele_data(data)
    tallenna_csv(data)

if __name__ == "__main__":
    main()