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

# API URL Euroopa riikide andmete jaoks
API_URL = "https://restcountries.com/v3.1/region/europe?fields=name,capital,population,area"


def extract():
    """
    Extract: loe REST API-st riikide andmed.

    Tagasta JSON andmed listina.

    Näide kuidas API-st andmeid pärida:
        response = requests.get("https://mingi-api.com/andmed")
        data = response.json()  # tagastab Pythoni listi/dict'i
    """
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()

    data = response.json()
    if data is None:
        raise ValueError("API returned no data")
    if not isinstance(data, list):
        raise ValueError(f"API returned unexpected type {type(data).__name__}, expected list")

    return data


def transform(raw_data):
    """
    Transform: puhasta ja normaliseeri andmed.

    Sisend: JSON list API-st (iga element on dict)
    Väljund: list tuple'itest kujul (name, capital, population, area, continent)

    Näide kuidas JSON-ist andmeid võtta:
        item = {"name": {"common": "Estonia"}, "capital": ["Tallinn"], "population": 1331057}
        nimi = item["name"]["common"]           # -> "Estonia"
        pealinn = item["capital"][0]            # -> "Tallinn"
        rahvaarv = item["population"]           # -> 1331057

    Sorteeri tulemus rahvaarvu järgi kahanevalt:
        rows.sort(key=lambda r: r[2], reverse=True)
    """
    # TODO: käi raw_data üle, võta igast elemendist vajalikud väljad, tagasta list tuple'itest
    result = []
    for item in raw_data:
        name = item["name"]["common"]
        capital = item["capital"][0] if "capital" in item and item["capital"] else None
        population = item["population"]
        area = item["area"]
        continent = "Europe"
        result.append((name, capital, population, area, continent))
    result.sort(key=lambda r: r[2], reverse=True)
    return result


def load(rows):
    """
    Load: kirjuta andmed PostgreSQL tabelisse europe_countries.

    Tabel peab sisaldama: id, name, capital, population, area_km2, continent, loaded_at
    Laadimine peab olema idempotentne (TRUNCATE enne laadimist).

    Näide kuidas PostgreSQL-iga ühenduda ja andmeid sisestada:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS test (id SERIAL PRIMARY KEY, name TEXT)")
        cur.execute("INSERT INTO test (name) VALUES (%s)", ("väärtus",))
        conn.commit()
        cur.close()
        conn.close()
    """
    # TODO: loo tabel, tühjenda see (TRUNCATE), sisesta andmed, kinnita (commit)
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS europe_countries (
            id SERIAL PRIMARY KEY,
            name TEXT,
            capital TEXT,
            population BIGINT,
            area_km2 REAL,
            continent TEXT,
            loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("TRUNCATE TABLE europe_countries")
    for row in rows:
        cur.execute("""
            INSERT INTO europe_countries (name, capital, population, area_km2, continent)
            VALUES (%s, %s, %s, %s, %s)
        """, row)
    conn.commit()
    cur.close()
    conn.close()


def main():
    print("=== ETL protsess ===\n")

    # Extract
    raw = extract()
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
