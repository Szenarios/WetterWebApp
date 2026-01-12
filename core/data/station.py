from core.data.DB import db
from math import radians, sin, atan2, cos, sqrt


class Station(db.Model):
    Station_ID = db.Column(db.Integer, primary_key=True)
    von_Datum = db.Column(db.Float)
    bis_Datum = db.Column(db.Float)
    Stationshoehe = db.Column(db.Float)
    geoBreite = db.Column(db.Float, index=True)
    geoLaenge = db.Column(db.Float, index=True)
    Stationsname = db.Column(db.String)
    Bundesland = db.Column(db.String)
    Abgabe = db.Column(db.String)


def haversine(lat1, lon1, lat2, lon2):  # Gibt die Luftlinie zurück -> Zwischen zwei Koordinaten
    R = 6371  # Erd-Radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


from sqlalchemy import and_

def get_stations_within_radius(lat, lon, radius_km):
    # Bounding Box (grob, km → Grad)
    lat_min = lat - radius_km / 111
    lat_max = lat + radius_km / 111
    lon_min = lon - radius_km / 71
    lon_max = lon + radius_km / 71

    # DB-Filter
    stations = Station.query.filter(
        and_(
            Station.geoBreite >= lat_min,
            Station.geoBreite <= lat_max,
            Station.geoLaenge >= lon_min,
            Station.geoLaenge <= lon_max
        )
    ).all()

    # Exakte Distanz prüfen
    result = []
    for s in stations:
        dist = haversine(lat, lon, s.geoBreite, s.geoLaenge)
        if dist <= radius_km:
            result.append(s.Station_ID)

    return result

