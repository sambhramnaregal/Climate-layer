document.getElementById('get-weather-btn').addEventListener('click', getWeather);

async function getWeather() {
    const latInput = document.getElementById('lat');
    const lonInput = document.getElementById('lon');
    const weatherResult = document.getElementById('weather-result');
    const errorMessage = document.getElementById('error-message');
    const loading = document.getElementById('loading');

    const lat = latInput.value;
    const lon = lonInput.value;

    // Reset UI
    weatherResult.classList.add('hidden');
    errorMessage.classList.add('hidden');

    if (!lat || !lon) {
        showError("Please enter both latitude and longitude.");
        return;
    }

    loading.classList.remove('hidden');

    try {
        const response = await fetch(`/api/weather?lat=${lat}&lon=${lon}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Failed to fetch weather data.");
        }

        displayWeather(data);
    } catch (error) {
        showError(error.message);
    } finally {
        loading.classList.add('hidden');
    }
}

function displayWeather(data) {
    const meta = data.metadata;
    const current = data.current;
    const hourly = data.hourly;

    // 1. Metadata
    setText('meta-lat', meta.latitude.toFixed(4));
    setText('meta-lon', meta.longitude.toFixed(4));
    setText('meta-elev', meta.elevation);
    setText('meta-offset', meta.utc_offset_seconds);

    // 2. Current
    setText('curr-temp', current.temperature_2m.toFixed(1));
    setText('curr-time', new Date(current.time * 1000).toLocaleString()); // Convert unix timestamp if it is one, openmeteo returns seconds since epoch for .Time()
    // Wait, open-meteo .Time() returns seconds. 
    // The previous python code: current.Time() returns int.
    // So distinct from UTC string.

    setText('curr-wind-speed', current.wind_speed_10m.toFixed(2));
    setText('curr-wind-dir', current.wind_direction_10m.toFixed(1));
    setText('curr-humidity', current.relative_humidity_2m.toFixed(1));
    setText('curr-precip', current.precipitation.toFixed(2));

    // 3. Hourly
    const tbody = document.querySelector('#hourly-table tbody');
    tbody.innerHTML = '';

    if (hourly && hourly.length > 0) {
        hourly.forEach(row => {
            const tr = document.createElement('tr');
            const dateCell = document.createElement('td');
            // 'date' in dataframe was datetime64, converted to string in python: "2024-05-22 14:00:00+00:00"
            dateCell.textContent = row.date;

            const radCell = document.createElement('td');
            radCell.textContent = parseFloat(row.direct_radiation_instant).toFixed(2);

            tr.appendChild(dateCell);
            tr.appendChild(radCell);
            tbody.appendChild(tr);
        });
    }

    document.getElementById('weather-result').classList.remove('hidden');
}

function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

function showError(message) {
    const errorMessage = document.getElementById('error-message');
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
}
