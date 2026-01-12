import threading

from flask import Flask, render_template, request, jsonify

from core.data import Measurement, station, beschreibungs_generator
from core.data.DB import db
from core.dataScraper import updateData
from flasgger import Swagger
from core.api_calls import api_bp

run_upload = False
app = Flask(__name__)
swagger = Swagger(app)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///weather.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


def loadDB():
    with app.app_context():
        db.create_all()
        updateData(db)


def to_float_date(val):
    if not val:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        val = val.replace("-", "")
        return float(val)
    return None


@app.route('/')
def index():
    return render_template('template.html')


@app.route('/get_weather', methods=['POST'])
def get_weather():
    data = request.get_json()
    lat = data.get('lat')
    lon = data.get('lon')
    radius = float(data.get('radius'))
    startDate = to_float_date(data.get("startDate"))
    endDate = to_float_date(data.get("endDate"))

    nearest_stations = station.get_stations_within_radius(lat, lon, radius)
    durchschnittDaten = Measurement.berechne_light_durchschnitt(nearest_stations, startDate, endDate)
    # Temperatur
    tmk = durchschnittDaten.get("avg_TMK")
    tmk = round(float(tmk), 1) if tmk is not None else None

    # Niederschlag
    rsk = durchschnittDaten.get("avg_RSK")
    rsk = round(float(rsk), 1) if rsk is not None else None

    # Wind
    fm = durchschnittDaten.get("avg_FM")
    fm = round(float(fm), 1) if fm is not None else None

    # Bewölkung
    nm = durchschnittDaten.get("avg_NM")
    nm = round(float(nm), 1) if nm is not None else None

    return jsonify({
        'temperature': tmk,
        'niederschlag': rsk,
        'location': f'{lat}, {lon}',
        'wind': beschreibungs_generator.generiere_wind_text(fm),
        'bewoelkung': beschreibungs_generator.generiere_bewoelkung_text(nm),
        'description': beschreibungs_generator.generiere_kurzbeschreibung(tmk, rsk, fm, nm)
    })


@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    lat = float(request.args.get('lat'))
    lon = float(request.args.get('lon'))
    radius = float(request.args.get('radius'))
    startDate = to_float_date(request.args.get("startDate"))
    endDate = to_float_date(request.args.get("endDate"))

    nearest_stations = station.get_stations_within_radius(lat, lon, radius)
    data = Measurement.getDataInRadiusAsJson(nearest_stations, startDate, endDate)

    return render_template("dashboard.html", data=data, lat=lat, lon=lon, radius=radius, start_date=startDate, end_date=endDate)


if __name__ == '__main__':
    if not run_upload:
        run_upload = True
        threading.Thread(target=loadDB, daemon=True, name="download").start()

    app.register_blueprint(api_bp)
    app.run(debug=False)
