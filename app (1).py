from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import joblib
import os

app = Flask(__name__)
app.secret_key = 'smartagriculturekey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smart_agriculture.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    humidity = db.Column(db.Float)
    temperature = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/sensor-data', methods=['POST'])
def receive_sensor_data():
    data = request.json
    sensor_entry = SensorData(humidity=data['humidity'], temperature=data['temperature'])
    db.session.add(sensor_entry)
    db.session.commit()
    return jsonify({'message': 'Sensor data stored successfully'})

@app.route('/api/latest-sensor', methods=['GET'])
def get_latest_sensor():
    latest = SensorData.query.order_by(SensorData.timestamp.desc()).first()
    if latest:
        return jsonify({
            'humidity': latest.humidity,
            'temperature': latest.temperature,
            'timestamp': latest.timestamp.isoformat()
        })
    return jsonify({'message': 'No data yet'}), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
