document.addEventListener('DOMContentLoaded', () => {
    const coordsInfo = document.getElementById('coordsInfo');
    const weatherDetails = document.getElementById('weatherDetails');
    const weatherInfoCard = document.getElementById('weather-info');
    const uploadForm = document.getElementById('uploadForm');
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');
    const slider = document.getElementById('radiusSlider');
    const radiusValue = document.getElementById('radiusValue');
    const reloadBtn = document.getElementById('reloadBtn');
    const dashboard_btn = document.getElementById('dashboard_btn');

    const germanyBounds = L.latLngBounds(
        [47.270111, 5.866342],
        [55.099161, 15.041896]
    );

    const map = L.map('map', {
        center: [51.1657, 10.4515],
        zoom: 6,
        maxBounds: germanyBounds,
        maxBoundsViscosity: 1.0,
        minZoom: 5
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap Contributors'
    }).addTo(map);

    const formatWeather = (data) => `
        <div class="grid gap-4 text-sm">
            <div class="rounded-2xl border border-white/5 bg-slate-950/60 p-3 shadow-inner shadow-black/30">
                <p class="text-xs uppercase tracking-[0.2em] text-slate-400">Ort</p>
                <p class="mt-2 text-lg font-semibold text-white">${data.location || 'Unbekannt'}</p>
            </div>

                <div class="rounded-2xl border border-white/5 bg-slate-950/60 p-3 shadow-inner shadow-black/30">
                    <p class="text-xs uppercase tracking-[0.2em] text-slate-400">Temperatur</p>
                    <p class="mt-3 text-2xl font-semibold text-white">${data.temperature || '—'}</p>
                </div>
                <div class="rounded-2xl border border-white/5 bg-slate-950/60 p-3 shadow-inner shadow-black/30">
                    <p class="text-xs uppercase tracking-[0.2em] text-slate-400">Niederschlag</p>
                    <p class="mt-3 text-lg font-semibold text-white">${data.niederschlag || '—'}</p>
                </div>
                <div class="rounded-2xl border border-white/5 bg-slate-950/60 p-3 shadow-inner shadow-black/30">
                    <p class="text-xs uppercase tracking-[0.2em] text-slate-400">Radius</p>
                    <p class="mt-3 text-lg font-semibold text-white">${slider ? `${slider.value} km` : '—'}</p>
                </div>

            <div class="rounded-2xl border border-white/5 bg-slate-950/60 p-3 shadow-inner shadow-black/30">
                <p class="text-xs uppercase tracking-[0.2em] text-slate-400">Wind</p>
                <p class="mt-3 text-lg font-semibold text-white">${data.wind || '—'}</p>
            </div>
            <div class="rounded-2xl border border-white/5 bg-slate-950/60 p-3 shadow-inner shadow-black/30">
                <p class="text-xs uppercase tracking-[0.2em] text-slate-400">Bewölkung</p>
                <p class="mt-3 text-lg font-semibold text-white">${data.bewoelkung || '—'}</p>
            </div>
            <div class="rounded-2xl border border-cyan-500/40 bg-cyan-500/10 p-3 text-sm text-cyan-100 backdrop-blur">
                <p class="text-xs uppercase tracking-[0.2em] text-cyan-300">Beschreibung</p>
                <p class="mt-2 leading-relaxed">${data.description || 'Keine weiteren Details verfügbar.'}</p>
            </div>

        </div>
    `;

    const renderWeather = (data) => {
        if (!weatherDetails) return;
        weatherDetails.innerHTML = formatWeather(data);
        weatherInfoCard?.style.setProperty('border-color', 'rgba(34, 211, 238, 0.4)');
    };

    const showWeatherPlaceholder = (message) => {
        if (!weatherDetails) return;
        weatherDetails.innerHTML = `
            <div class="rounded-2xl border border-white/5 bg-slate-950/60 p-6 shadow-inner shadow-black/30 text-sm text-slate-300">
                ${message}
            </div>
        `;
        weatherInfoCard?.style.setProperty('border-color', 'rgba(255, 255, 255, 0.05)');
    };

    const updateLocationInfo = async (lat, lng) => {
        if (!coordsInfo) return;
        coordsInfo.textContent = 'Suche Adresse…';
        try {
            const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lng}`);
            const data = await response.json();
            const region = data.address?.state || data.address?.region || 'unbekannt';
            const country = data.address?.country || 'unbekannt';
            const city = data.address?.city || data.address?.town || data.address?.village || data.address?.municipality || 'unbekannt';
            coordsInfo.textContent = `${city}, ${region}, ${country}`;
        } catch (error) {
            console.error('Reverse geocoding failed', error);
            coordsInfo.textContent = 'Region konnte nicht ermittelt werden';
        }
    };

    const updateSliderVisual = (value) => {
        if (!slider) return;
        const min = Number(slider.min) || 0;
        const max = Number(slider.max) || 100;
        const val = Number(value);
        const percentage = ((val - min) / (max - min)) * 100;
        slider.style.setProperty('--fill', `${percentage}%`);
        if (radiusValue) {
            radiusValue.textContent = `${val} km`;
        }
    };

    if (slider) {
        updateSliderVisual(slider.value);
        slider.addEventListener('input', (event) => {
            updateSliderVisual(event.target.value);
        });
    }

    if (reloadBtn) {
        reloadBtn.addEventListener('click', () => {
            window.location.reload();
        });
    }

    if (dashboard_btn) {
        dashboard_btn.addEventListener('click', () => {
            if (!marker){
                alert('Wähle zuerst einen Standort aus!');
                return
            }
            var latLng = marker.getLatLng();
            var lat = latLng.lat
            var lng = latLng.lng
            var radius = slider.value
            const startDate = startDateInput?.value;
            const endDate = endDateInput?.value;

            if (!startDate || !endDate) {
                alert('Bitte Start- und Enddatum auswählen.');
                return;
            }

            if (new Date(startDate) > new Date(endDate)) {
                alert('Das Enddatum muss nach dem Startdatum liegen.');
                return;
            }

            const url = `/dashboard?lat=${lat}&lon=${lng}&radius=${radius}&startDate=${startDate}&endDate=${endDate}`;

            // Weiterleiten
            window.location.href = url;
        });
    }

    if (uploadForm) {
        uploadForm.addEventListener('submit', (event) => {
            event.preventDefault();
            const formData = new FormData(uploadForm);
            console.log(formData);
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
                .then((res) => {
                    if (!res.ok) {
                        throw new Error('Upload fehlgeschlagen');
                    }
                    return res.text();
                })
                .then((message) => {
                    alert(message);
                    uploadForm.reset();
                })
                .catch((error) => {
                    console.error(error);
                    alert('Da ist etwas schiefgelaufen. Bitte erneut versuchen.');
                });
        });
    }

    let marker;

    map.on('click', async (event) => {
        const { lat, lng } = event.latlng;

        const startDate = startDateInput?.value;
        const endDate = endDateInput?.value;

        if (!startDate || !endDate) {
            alert('Bitte Start- und Enddatum auswählen.');
            return;
        }

        if (new Date(startDate) > new Date(endDate)) {
            alert('Das Enddatum muss nach dem Startdatum liegen.');
            return;
        }

        if (marker) {
            map.removeLayer(marker);
        }

        marker = L.marker([lat, lng], { draggable: true }).addTo(map);
        await updateLocationInfo(lat, lng);

        marker.on('dragend', async (ev) => {
            const position = ev.target.getLatLng();
            await updateLocationInfo(position.lat, position.lng);
        });

        fetch('/get_weather', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                lat,
                lon: lng,
                radius: slider ? slider.value : null,
                startDate,
                endDate
            })
        })
            .then((res) => {
                if (!res.ok) {
                    throw new Error('Wetterdaten konnten nicht geladen werden');
                }
                return res.json();
            })
            .then((data) => {
                renderWeather(data);
            })
            .catch((error) => {
                console.error(error);
                showWeatherPlaceholder('Aktuell sind keine Wetterdaten verfügbar. Bitte versuche es später erneut.');
            });
    });

    showWeatherPlaceholder('Bitte wähle einen Zeitraum und setze anschließend einen Marker in der Karte.');
});
