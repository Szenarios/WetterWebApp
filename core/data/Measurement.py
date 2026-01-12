import json

from sqlalchemy import func

from core.data.DB import db


class measurement(db.Model):
    measurement_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    station_ID = db.Column(db.Integer, db.ForeignKey('station.Station_ID'), index=True)  # Beispiel für ForeignKey

    measurement_Datum = db.Column(db.Float, index=True)
    QN_3 = db.Column(db.Float)
    FX = db.Column(db.Float)
    FM = db.Column(db.Float)
    QN_4 = db.Column(db.Float)
    RSK = db.Column(db.Float)
    RSKf = db.Column(db.Float)
    SDK = db.Column(db.Float)
    SHK_TAG = db.Column(db.Float)
    NM = db.Column(db.Float)
    VPM = db.Column(db.Float)
    PM = db.Column(db.Float)
    TMK = db.Column(db.Float)
    UPM = db.Column(db.Float)
    TXK = db.Column(db.Float)
    TNK = db.Column(db.Float)
    TGK = db.Column(db.Float)
    eor = db.Column(db.String)

    __table_args__ = (
        db.Index("idx_station_date", "station_ID", "measurement_Datum"),
    )


def count_items_by_station(search_station_id):
    return db.session.query(measurement).filter_by(station_ID=search_station_id).count()


def berechne_light_durchschnitt(station_ids, start_date=None, end_date=None):
    """
    Berechnet den Durchschnitt aller numerischen Spalten für die angegebenen Stationen
    und optional für einen bestimmten Zeitraum.

    :param station_ids: Liste von Station-IDs
    :param start_date: Startdatum (Float oder String, z.B. '20230101')
    :param end_date: Enddatum (Float oder String, z.B. '20231231')
    :return: Dictionary mit Spaltennamen und Durchschnittswerten
    """
    query = db.session.query(
        # func.avg(measurement.QN_3).label('avg_QN_3'),
        # func.avg(measurement.FX).label('avg_FX'),
        func.avg(measurement.FM).label('avg_FM'),
        # func.avg(measurement.QN_4).label('avg_QN_4'),
        func.avg(measurement.RSK).label('avg_RSK'),
        # func.avg(measurement.RSKf).label('avg_RSKf'),
        # func.avg(measurement.SDK).label('avg_SDK'),
        # func.avg(measurement.SHK_TAG).label('avg_SHK_TAG'),
        func.avg(measurement.NM).label('avg_NM'),
        # func.avg(measurement.VPM).label('avg_VPM'),
        # func.avg(measurement.PM).label('avg_PM'),
        func.avg(measurement.TMK).label('avg_TMK')
        # func.avg(measurement.UPM).label('avg_UPM')
        # func.avg(measurement.TXK).label('avg_TXK'),
        # func.avg(measurement.TNK).label('avg_TNK'),
        # func.avg(measurement.TGK).label('avg_TGK')
    ).filter(measurement.station_ID.in_(station_ids))

    # Zeitraum-Filter hinzufügen
    if start_date:
        query = query.filter(measurement.measurement_Datum >= float(start_date))
    if end_date:
        query = query.filter(measurement.measurement_Datum <= float(end_date))

    result = query.one()
    return {col: getattr(result, col) for col in result._fields}


def berechne_durchschnitt(station_ids, start_date=None, end_date=None):
    """
    Berechnet den Durchschnitt aller numerischen Spalten für die angegebenen Stationen
    und optional für einen bestimmten Zeitraum.

    :param station_ids: Liste von Station-IDs
    :param start_date: Startdatum (Float oder String, z.B. '20230101')
    :param end_date: Enddatum (Float oder String, z.B. '20231231')
    :return: Dictionary mit Spaltennamen und Durchschnittswerten
    """
    query = db.session.query(
        func.avg(measurement.QN_3).label('avg_QN_3'),
        func.avg(measurement.FX).label('avg_FX'),
        func.avg(measurement.FM).label('avg_FM'),
        func.avg(measurement.QN_4).label('avg_QN_4'),
        func.avg(measurement.RSK).label('avg_RSK'),
        func.avg(measurement.RSKf).label('avg_RSKf'),
        func.avg(measurement.SDK).label('avg_SDK'),
        func.avg(measurement.SHK_TAG).label('avg_SHK_TAG'),
        func.avg(measurement.NM).label('avg_NM'),
        func.avg(measurement.VPM).label('avg_VPM'),
        func.avg(measurement.PM).label('avg_PM'),
        func.avg(measurement.TMK).label('avg_TMK'),
        func.avg(measurement.UPM).label('avg_UPM'),
        func.avg(measurement.TXK).label('avg_TXK'),
        func.avg(measurement.TNK).label('avg_TNK'),
        func.avg(measurement.TGK).label('avg_TGK')
    ).filter(measurement.station_ID.in_(station_ids))

    # Zeitraum-Filter hinzufügen
    if start_date:
        query = query.filter(measurement.measurement_Datum >= start_date)
    if end_date:
        query = query.filter(measurement.measurement_Datum <= end_date)

    result = query.one()
    return {col: getattr(result, col) for col in result._fields}


def getDataInRadiusAsJson(station_ids, start_date=None, end_date=None):
    results = db.session.query(measurement).filter(
        measurement.station_ID.in_(station_ids),
        measurement.measurement_Datum.between(start_date, end_date)
    ).all()

    def convertDate(date):
        try:
            date = str(int(date))
            date = f"{date[:4]}-{date[4:6]}-{date[6:]}"
        except:
            print(f"Datum '{date}' konnte nicht zu einem String Convertiert werden!")

        return date

    # Ergebnisse in ein JSON-kompatibles Format umwandeln
    def measurement_to_dict(m):
        return {
            "measurement_ID": m.measurement_ID,
            "station_ID": m.station_ID,
            "measurement_Datum": convertDate(m.measurement_Datum),
            "QN_3": m.QN_3,
            "FX": m.FX,
            "FM": m.FM,
            "QN_4": m.QN_4,
            "RSK": m.RSK,
            "RSKf": m.RSKf,
            "SDK": m.SDK,
            "SHK_TAG": m.SHK_TAG,
            "NM": m.NM,
            "VPM": m.VPM,
            "PM": m.PM,
            "TMK": m.TMK,
            "UPM": m.UPM,
            "TXK": m.TXK,
            "TNK": m.TNK,
            "TGK": m.TGK,
            "eor": m.eor
        }

    results_json = [measurement_to_dict(m) for m in results]

    # Ausgabe
    return results_json


def measurement_to_compact_json(measurements):
    # Welche Felder du behalten willst
    fields = [
        "measurement_Datum", "station_ID", "QN_3", "FX", "FM", "QN_4", "RSK", "RSKf",
        "SDK", "SHK_TAG", "NM", "VPM", "PM", "TMK", "UPM", "TXK", "TNK", "TGK"
    ]

    compact_data = {
        "columns": [  # hübsche Spaltennamen
            "measurement_Datum", "station_ID", "QN_3", "FX", "FM", "QN_4", "RSK", "RSKf",
            "SDK", "SHK_TAG", "NM", "VPM", "PM", "TMK", "UPM", "TXK", "TNK", "TGK"
        ],
        "data": []
    }

    for m in measurements:
        row = []
        for f in fields:
            val = getattr(m, f)
            if f == "measurement_Datum":
                val = convertDate(val)  # YYYY-MM-DD
            # runde alle Werte auf 2 Nachkommastellen
            if isinstance(val, float):
                val = round(val, 2)
            row.append(val)
        compact_data["data"].append(row)

    return compact_data
