import csv
import os
import zipfile
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from sqlalchemy import text

from core.data.Measurement import measurement
from core.data.station import Station

download_folder = "downloads"
file_extensions = ['.txt', '.zip']
url = "https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/daily/kl/historical/"


def updateData(db):
    download_files_from_url(url)
    # Put DB
    lade_stationen_aus_datei(db, f"{download_folder}/KL_Tageswerte_Beschreibung_Stationen.txt")

    entpackeFile(db=db)


def download_files_from_url(base_url):
    os.makedirs(download_folder, exist_ok=True)

    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    downloaded_files = []

    for link in soup.find_all('a', href=True):
        file_url = urljoin(base_url, link['href'])
        if any(file_url.lower().endswith(ext) for ext in file_extensions):
            downloaded_files += writeFile(file_url)
    return downloaded_files


def entpackeFile(db):
    for file in Path(download_folder).iterdir():
        if file.name.lower().endswith(".zip"):
            with zipfile.ZipFile(download_folder + "/" + file.name, 'r') as zip_ref:
                for files in zip_ref.filelist:
                    if files.filename.lower().startswith("produkt_klima_tag"):
                        lade_messdaten_in_db(download_folder + "/" + file.name, files.filename, db)


def writeFile(file_url):
    downloaded_files = []
    filename = os.path.basename(file_url)
    filepath = os.path.join(download_folder, filename)

    if not Path(filepath).exists():
        try:
            file_response = requests.get(file_url)
            with open(filepath, 'wb') as f:
                f.write(file_response.content)
            downloaded_files.append(filename)
            print(f"Heruntergeladen: {filename}")
        except Exception as e:
            print(f"Fehler beim Herunterladen von {file_url}: {e}")
    else:
        print(f"Datei exestiert bereits {filepath}")
    return downloaded_files


def lade_stationen_aus_datei(db, pfad):
    with open(pfad) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 9 or not parts[0].isdigit():
                continue  # Überspringe Header oder ungültige Zeilen

            try:
                station = Station(
                    Station_ID=int(parts[0]),
                    von_Datum=parts[1],
                    bis_Datum=parts[2],
                    Stationshoehe=int(parts[3]),
                    geoBreite=float(parts[4]),
                    geoLaenge=float(parts[5]),
                    Stationsname=' '.join(parts[6:-2]),
                    Bundesland=parts[-2],
                    Abgabe=parts[-1]
                )

                existing = Station.query.filter_by(Station_ID=int(parts[0])).first()
                if not existing:
                    db.session.add(station)
            except Exception as e:
                print(f"Etwas ist schief gelaufen beim Konvertieren von Datei zu DB daten in {parts}")
                print(e)
        db.session.commit()
        print("Stationen erfolgreich importiert.")


def lade_messdaten_in_db(dateipfad: str, dateiname: str, db):
    with zipfile.ZipFile(dateipfad, 'r') as zip_ref:
        with zip_ref.open(dateiname) as file:
            reader = csv.reader(file.read().decode('utf-8').splitlines(), delimiter=';')
            header = next(reader)  # Header überspringen

            # Station-ID aus erster Datenzeile
            first_line = next(reader)
            station_id = int(first_line[0])
            # Erste Zeile wieder hinzufügen
            reader = [first_line] + list(reader)

            # PRAGMA für Performance
            db.session.execute(text("PRAGMA synchronous = OFF"))
            db.session.execute(text("PRAGMA journal_mode = MEMORY"))

            # Existierende Datumswerte für diese Station laden

            existing_keys = {

                (sid, date)
                for sid, date in db.session.query(
                    measurement.station_ID, measurement.measurement_Datum
                ).filter_by(station_ID=station_id)
            }

            rows = []
            CHUNK_SIZE = 10_000

            def parse_float(val):
                if val in (None, "", "-999.0", "-999", "-9999"):
                    return None

                try:
                    num = float(str(val).replace(",", "."))
                except ValueError:
                    return None

                # Alle ungültigen DWD-Werte unter -900 abfangen
                if num <= -900:
                    return None

                return num

            print(f"Lade Daten für Station [{station_id}]...")

            for parts in reader:
                if len(parts) < 19:
                    continue

                key = (int(parts[0]), float(parts[1]))
                if key in existing_keys:
                    continue  # Daten existieren schon

                rows.append({
                    'station_ID': int(parts[0]),
                    'measurement_Datum': parts[1],
                    'QN_3': parse_float(parts[2]),
                    'FX': parse_float(parts[3]),
                    'FM': parse_float(parts[4]),
                    'QN_4': parse_float(parts[5]),
                    'RSK': parse_float(parts[6]),
                    'RSKf': parse_float(parts[7]),
                    'SDK': parse_float(parts[8]),
                    'SHK_TAG': parse_float(parts[9]),
                    'NM': parse_float(parts[10]),
                    'VPM': parse_float(parts[11]),
                    'PM': parse_float(parts[12]),
                    'TMK': parse_float(parts[13]),
                    'UPM': parse_float(parts[14]),
                    'TXK': parse_float(parts[15]),
                    'TNK': parse_float(parts[16]),
                    'TGK': parse_float(parts[17]),
                    'eor': parts[18]
                })

                if len(rows) >= CHUNK_SIZE:
                    db.session.bulk_insert_mappings(measurement, rows)
                    db.session.commit()
                    rows.clear()

            # Rest einfügen
            if rows:
                db.session.bulk_insert_mappings(measurement, rows)
                db.session.commit()
