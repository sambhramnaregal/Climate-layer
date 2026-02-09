from flask import Flask, render_template, request, jsonify
from temperature import get_weather

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/weather', methods=['GET'])
def weather_route():
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    if not lat or not lon:
        return jsonify({"error": "Latitude and Longitude are required"}), 400

    # Ensure lat/lon are floats
    try:
        lat = float(lat)
        lon = float(lon)
    except ValueError:
        return jsonify({"error": "Latitude and Longitude must be numbers"}), 400

    data = get_weather(lat, lon)
    
    if "error" in data:
         return jsonify(data), 500

    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
