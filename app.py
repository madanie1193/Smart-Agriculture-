
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import joblib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smart_agriculture.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# -----------------------------
# DATABASE MODELS
# -----------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    humidity = db.Column(db.Float)
    temperature = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class CropPrediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crop = db.Column(db.String(50))
    input_data = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class PricePrediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crop = db.Column(db.String(50))
    predicted_price = db.Column(db.Float)
    input_data = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# -----------------------------
# AUTH ROUTES
# -----------------------------
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    hashed_password = generate_password_hash(data['password'])
    new_user = User(username=data['username'], password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password_hash, data['password']):
        return jsonify({'message': 'Login successful'})
    return jsonify({'message': 'Invalid credentials'}), 401

# -----------------------------
# SENSOR DATA ROUTE
# -----------------------------
@app.route('/sensor-data', methods=['POST'])
def receive_sensor_data():
    data = request.json
    sensor_entry = SensorData(humidity=data['humidity'], temperature=data['temperature'])
    db.session.add(sensor_entry)
    db.session.commit()
    return jsonify({'message': 'Sensor data stored successfully'})

# -----------------------------
# CROP PREDICTION ROUTE
# -----------------------------
@app.route('/predict-crop', methods=['POST'])
def predict_crop():
    data = request.json
    model = joblib.load('models/crop_model.pkl')
    prediction = model.predict([data['features']])[0]
    db.session.add(CropPrediction(crop=prediction, input_data=str(data['features'])))
    db.session.commit()
    return jsonify({'predicted_crop': prediction})

# -----------------------------
# PRICE PREDICTION ROUTE
# -----------------------------
@app.route('/predict-price', methods=['POST'])
def predict_price():
    data = request.json
    model = joblib.load('models/price_model.pkl')
    prediction = model.predict([data['features']])[0]
    db.session.add(PricePrediction(crop=data['crop'], predicted_price=prediction, input_data=str(data['features'])))
    db.session.commit()
    return jsonify({'predicted_price': prediction})

# -----------------------------
# INIT DB
# -----------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
