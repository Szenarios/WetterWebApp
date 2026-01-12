def generiere_temperatur_text(tmk):
    # Temperatur
    if tmk is not None:
        if tmk < 0:
            return "Frostig"
        elif tmk < 10:
            return "Kühl"
        elif tmk < 20:
            return "Mild"
        else:
            return "Warm"
    else:
        return "--"

def generiere_niederschlag_text(rsk):
    # Niederschlag
    if rsk is not None:
        if rsk == 0:
            return "Trocken"
        elif rsk < 1:
            return "Leichter Niederschlag"
        elif rsk < 5:
            return "Mäßiger Niederschlag"
        else:
            return "Starker Niederschlag"
    else:
        return "--"

def generiere_wind_text(fm):
    # Wind
    if fm is not None:
        if fm < 2:
            return "Windstill"
        elif fm < 5:
            return "Leichter Wind"
        else:
            return "Starker Wind"
    else:
        return "--"

def generiere_bewoelkung_text(nm):
    # Optional: Sonnenschein / Bewölkung
    if nm is not None:
        if nm < 3:
            return "Sonnig"
        elif nm < 6:
            return "Teilweise bewölkt"
        else:
            return "Bewölkt"
    else:
        return "--"

def generiere_kurzbeschreibung(tmk, rsk, fm, nm):
    """
    Generiert eine kurze Wetterbeschreibung anhand von Durchschnittswerten.
    Nutzt nur TMK, RSK und FM (optional NM).
    """
    beschreibung = []

    beschreibung.append(generiere_temperatur_text(tmk))
    beschreibung.append(generiere_niederschlag_text(rsk))
    beschreibung.append(generiere_bewoelkung_text(fm))
    beschreibung.append(generiere_wind_text(fm))

    return ", ".join(beschreibung)
