from flask import Blueprint, jsonify, request
from sqlalchemy import func

from core.data.Measurement import measurement
from core.data.station import Station
from core.data.DB import db

api_bp = Blueprint('api', __name__, url_prefix='/api')

# ------------------------------
# 1. Alle Messungen
# ------------------------------
@api_bp.route('/measurements', methods=['GET'])
def get_all_measurements():
    """
    Alle Messungen abrufen
    ---
    responses:
      200:
        description: Liste aller Messungen
    """
    measurements = measurement.query.all()
    result = []
    for m in measurements:
        result.append({
            "measurement_ID": m.measurement_ID,
            "station_ID": m.station_ID,
            "measurement_Datum": m.measurement_Datum,
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
        })
    return jsonify(result)


# ------------------------------
# 2. Messungen nach Station
# ------------------------------
@api_bp.route('/measurements/station/<int:station_id>', methods=['GET'])
def get_measurements_by_station(station_id):
    """
    Messungen einer bestimmten Station abrufen
    ---
    parameters:
      - name: station_id
        in: path
        type: integer
        required: true
        description: ID der Station
    responses:
      200:
        description: Liste der Messungen für die Station
    """
    measurements = measurement.query.filter_by(station_ID=station_id).all()
    result = [{"measurement_ID": m.measurement_ID, "measurement_Datum": m.measurement_Datum, "QN_3": m.QN_3} for m in measurements]
    return jsonify(result)


# ------------------------------
# 3. Alle Stationen
# ------------------------------
@api_bp.route('/stations', methods=['GET'])
def get_all_stations():
    """
    Alle Stationen abrufen
    ---
    responses:
      200:
        description: Liste aller Stationen
    """
    stations = Station.query.all()
    result = []
    for s in stations:
        result.append({
            "Station_ID": s.Station_ID,
            "Stationsname": s.Stationsname,
            "von_Datum": s.von_Datum,
            "bis_Datum": s.bis_Datum,
            "Stationshoehe": s.Stationshoehe,
            "geoBreite": s.geoBreite,
            "geoLaenge": s.geoLaenge,
            "Bundesland": s.Bundesland,
            "Abgabe": s.Abgabe
        })
    return jsonify(result)


# ------------------------------
# 4. Einzelne Station
# ------------------------------
@api_bp.route('/stations/<int:station_id>', methods=['GET'])
def get_station(station_id):
    """
    Einzelne Station abrufen
    ---
    parameters:
      - name: station_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Stationendetails
    """
    s = Station.query.get_or_404(station_id)
    return jsonify({
        "Station_ID": s.Station_ID,
        "Stationsname": s.Stationsname,
        "von_Datum": s.von_Datum,
        "bis_Datum": s.bis_Datum,
        "Stationshoehe": s.Stationshoehe,
        "geoBreite": s.geoBreite,
        "geoLaenge": s.geoLaenge,
        "Bundesland": s.Bundesland,
        "Abgabe": s.Abgabe
    })


# ------------------------------
# 5. Messungen nach Datum
# ------------------------------
@api_bp.route('/measurements/date', methods=['GET'])
def get_measurements_by_date():
    """
    Messungen nach Zeitraum filtern
    ---
    parameters:
      - name: start
        in: query
        type: number
        required: false
        description: Startdatum (Float)
      - name: end
        in: query
        type: number
        required: false
        description: Enddatum (Float)
    responses:
      200:
        description: Liste der Messungen im Zeitraum
    """
    start = request.args.get('start', type=float)
    end = request.args.get('end', type=float)
    query = measurement.query
    if start is not None:
        query = query.filter(measurement.measurement_Datum >= start)
    if end is not None:
        query = query.filter(measurement.measurement_Datum <= end)
    measurements = query.all()
    result = [{"measurement_ID": m.measurement_ID, "measurement_Datum": m.measurement_Datum} for m in measurements]
    return jsonify(result)


# ------------------------------
# 6. Active Duration einer Station
# ------------------------------
@api_bp.route('/stations/<int:station_id>/active_duration', methods=['GET'])
def get_station_active_duration(station_id):
    """
    Dauer der Aktivität einer Station
    ---
    parameters:
      - name: station_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Dauer der Aktivität (Differenz von bis_Datum - von_Datum)
    """
    s = Station.query.get_or_404(station_id)
    if s.von_Datum is None or s.bis_Datum is None:
        return jsonify({"error": "Station hat keine Aktivitätsdaten"}), 400
    duration = s.bis_Datum - s.von_Datum
    return jsonify({"Station_ID": station_id, "Stationsname": s.Stationsname, "active_duration": duration})


# ------------------------------
# 7. Durchschnittliche Messungen (Zeitraum)
# ------------------------------
@api_bp.route('/measurements/average', methods=['GET'])
def get_average_measurements():
    """
    Durchschnittliche Messungen in einem Zeitraum
    ---
    parameters:
      - name: start
        in: query
        type: number
        required: false
      - name: end
        in: query
        type: number
        required: false
    responses:
      200:
        description: Durchschnittswerte
    """
    start = request.args.get('start', type=float)
    end = request.args.get('end', type=float)
    query = db.session.query(
        func.avg(measurement.QN_3).label("avg_QN_3"),
        func.avg(measurement.FX).label("avg_FX"),
        func.avg(measurement.FM).label("avg_FM"),
        func.avg(measurement.TMK).label("avg_TMK")
    )
    if start is not None:
        query = query.filter(measurement.measurement_Datum >= start)
    if end is not None:
        query = query.filter(measurement.measurement_Datum <= end)
    avg = query.one()
    return jsonify({"avg_QN_3": avg.avg_QN_3, "avg_FX": avg.avg_FX, "avg_FM": avg.avg_FM, "avg_TMK": avg.avg_TMK})


# ------------------------------
# 8. Durchschnittliche Messungen nach Station
# ------------------------------
@api_bp.route('/measurements/average/station/<int:station_id>', methods=['GET'])
def get_average_measurements_by_station(station_id):
    """
    Durchschnittliche Messungen einer Station in einem Zeitraum
    ---
    parameters:
      - name: station_id
        in: path
        type: integer
        required: true
      - name: start
        in: query
        type: number
        required: false
      - name: end
        in: query
        type: number
        required: false
    responses:
      200:
        description: Durchschnittswerte für die Station
    """
    start = request.args.get('start', type=float)
    end = request.args.get('end', type=float)
    query = db.session.query(
        func.avg(measurement.QN_3).label("avg_QN_3"),
        func.avg(measurement.FX).label("avg_FX"),
        func.avg(measurement.FM).label("avg_FM"),
        func.avg(measurement.TMK).label("avg_TMK")
    ).filter(measurement.station_ID == station_id)
    if start is not None:
        query = query.filter(measurement.measurement_Datum >= start)
    if end is not None:
        query = query.filter(measurement.measurement_Datum <= end)
    avg = query.one()
    return jsonify({"Station_ID": station_id, "avg_QN_3": avg.avg_QN_3, "avg_FX": avg.avg_FX, "avg_FM": avg.avg_FM, "avg_TMK": avg.avg_TMK})


# ------------------------------
# 9. Negative Temperaturen
# ------------------------------
@api_bp.route('/measurements/temperature/negative', methods=['GET'])
def get_negative_temperatures():
    """
    Alle negativen Temperaturwerte
    ---
    responses:
      200:
        description: Liste der Messungen mit TMK < 0
    """
    measurements = measurement.query.filter(measurement.TMK < 0).all()
    result = [{"measurement_ID": m.measurement_ID, "TMK": m.TMK, "station_ID": m.station_ID} for m in measurements]
    return jsonify(result)


# ------------------------------
# 10. Positive Temperaturen
# ------------------------------
@api_bp.route('/measurements/temperature/positive', methods=['GET'])
def get_positive_temperatures():
    """
    Alle positiven Temperaturwerte
    ---
    responses:
      200:
        description: Liste der Messungen mit TMK > 0
    """
    measurements = measurement.query.filter(measurement.TMK > 0).all()
    result = [{"measurement_ID": m.measurement_ID, "TMK": m.TMK, "station_ID": m.station_ID} for m in measurements]
    return jsonify(result)
