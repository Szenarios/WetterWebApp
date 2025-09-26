document.addEventListener('DOMContentLoaded', () => {
    const weatherInfo = document.getElementById('weather-info');
    const uploadForm = document.getElementById('uploadForm');

    const coordsInfo = document.getElementById('coordsInfo');

    const startDateInput = document.getElementById("startDate");
    const endDateInput = document.getElementById("endDate");
    const dateBtn = document.getElementById("dateBtn");

    const germanyBounds = L.latLngBounds(
      [47.270111, 5.866342],
      [55.099161, 15.041896]
    );

    const map = L.map('map', {
      center: [51.1657, 10.4515],
      zoom: 6,
      maxBounds: germanyBounds,
      maxBoundsViscosity: 1.0,
      minZoom: 6
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap Contributors'
    }).addTo(map);

    let marker;

    map.on('click', async function(e) {
        const { lat, lng } = e.latlng;

        if (marker) {
            map.removeLayer(marker);
        }
        // Datum Check
        const startDate = startDateInput.value; // z. B. "2025-09-26"
        const endDate = endDateInput.value;

        if (!startDate || !endDate) {
            alert("Bitte Start- und Enddatum auswählen!");
            return;
        }

        //alert(`Startdatum: ${startDate}, Enddatum: ${endDate}`);
        // Datum Check
        marker = L.marker([lat, lng], { draggable: true }).addTo(map);
        async function updateLocationInfo(lat, lng) {
            try {
                const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lng}`);
                const data = await response.json();
                const region = data.address.state || data.address.region || "unbekannt";
                const country = data.address.country || "unbekannt";
                const city = data.address.city || data.address.town || data.address.village || data.address.municipality || "unbekannt";
                coordsInfo.textContent = `${city}, ${region}, ${country}`;
            } catch (error) {
                coordsInfo.textContent = `Region/Land konnte nicht ermittelt werden`;
                console.error(error);
            }
        }

        // Erster Aufruf beim Klick
        updateLocationInfo(lat, lng);

        marker.on("dragend", function(ev) {
            const newLat = ev.target.getLatLng().lat;
            const newLng = ev.target.getLatLng().lng;
            updateLocationInfo(newLat, newLng);
        });

        // Wetterdaten abrufen
        fetch('/get_weather', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lat, lon: lng })
        })
        .then(res => res.json())
        .then(data => {
            weatherInfo.innerHTML = `
                <h2>Wetterdaten</h2>
                <p><strong>Ort:</strong> ${data.location}</p>
                <p><strong>Temperatur:</strong> ${data.temperature}</p>
                <p><strong>Luftfeuchtigkeit:</strong> ${data.humidity}</p>
                <p><strong>Beschreibung:</strong> ${data.description}</p>
            `;
        });
    });

    uploadForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const formData = new FormData(uploadForm);
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(res => res.text())
        .then(data => {
            alert(data);
        });
    });
});
