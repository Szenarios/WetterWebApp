from main import db


class Station(db.dataentry):
    Station_ID = db.Colum(db.Integer, primary_key=True)
    von_Datum = db.Colum(db.Float)
    bis_Datum = db.Colum(db.Float)
    Stationshoehe = db.Colum(db.Float)
    geoBreite = db.Colum(db.Float)
    geoLaenge = db.Colum(db.Float)
    Stationsname = db.Colum(db.String)
    Bundesland = db.Colum(db.String)
    Abgabe = db.Colum(db.String)
