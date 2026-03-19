"""
ETL skripti mall: loeb REST API-st andmeid ja laeb need PostgreSQL andmebaasi.

Ülesanne: täida extract(), transform() ja load() funktsioonid.
"""

import requests
import psycopg2
import os

# Andmebaasi ühenduse seaded (loetakse keskkonnamuutujatest)
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.environ["POSTGRES_DB"],
    "user": os.environ["POSTGRES_USER"],
    "password": os.environ["POSTGRES_PASSWORD"],
}

def extract(API_URL):
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()

    data = response.json()
    if data is None:
        raise ValueError("API returned no data")
    if not isinstance(data, list):
        raise ValueError(f"API returned unexpected type {type(data).__name__}, expected list")

    return data


def transform(raw_data):
    # TODO: käi raw_data üle, võta igast elemendist vajalikud väljad, tagasta list tuple'itest
    result = []
    for item in raw_data:
        name = item["name"]["common"]
        capital = item["capital"][0] if "capital" in item and item["capital"] else None
        population = item["population"]
        area = item["area"]
        continent = item["region"] if "region" in item else None
        result.append((name, capital, population, area, continent))
    result.sort(key=lambda r: r[2], reverse=True)
    return result


def load(rows):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS countries (
            id SERIAL PRIMARY KEY,
            name TEXT,
            capital TEXT,
            population BIGINT,
            area_km2 REAL,
            continent TEXT,
            loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    for row in rows:
        cur.execute("""
            INSERT INTO countries (name, capital, population, area_km2, continent)
            VALUES (%s, %s, %s, %s, %s)
        """, row)
    conn.commit()
    cur.close()
    conn.close()


def main():
    print("=== ETL protsess ===\n")

    regions = ['Europe', 'Asia', 'Africa']
    for region in regions:
        print(f"Processing region: {region}")
        API_URL = f"https://restcountries.com/v3.1/region/{region}?fields=name,capital,population,area,region"

        # Extract
        raw = extract(API_URL)
        if raw is None:
            raise SystemExit("Extract returned no data")

        print(f"Extracted: {len(raw)} kirjet\n")

        # Transform
        rows = transform(raw)
        print(f"Transformed: {len(rows)} rida\n")

        # Load
        load(rows)
        
    print("\n=== ETL lõpetatud ===")


if __name__ == "__main__":
    main()
