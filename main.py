from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)



from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('template.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    # Hier kannst du die Datei analysieren und Daten in DB schreiben
    return 'File uploaded successfully', 200

@app.route('/get_weather', methods=['POST'])
def get_weather():
    data = request.get_json()
    lat = data.get('lat')
    lon = data.get('lon')
    # Beispielantwort – hier kannst du deine echte Logik einsetzen
    return jsonify({
        'temperature': '21°C',
        'humidity': '50%',
        'location': f'{lat}, {lon}',
        'description': 'Teilweise bewölkt'
    })

if __name__ == '__main__':
    app.run(debug=True)
