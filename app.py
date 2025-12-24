from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import json
from database import Database
from sensor_simulator import SensorSimulator
from ml_models import VehicleHealthAI
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'dev-secret-key')
CORS(app)

db = Database()
simulator = SensorSimulator()
ai_model = VehicleHealthAI()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/current-status')
def get_current_status():
    sensor_data = simulator.generate_sensor_reading()
    
    health_score = ai_model.calculate_health_score(sensor_data)
    anomalies = ai_model.detect_anomalies(sensor_data)
    predictions = ai_model.predict_maintenance(sensor_data)
    
    db.log_sensor_data(sensor_data)
    
    status = 'healthy'
    if health_score < 50:
        status = 'critical'
    elif health_score < 75:
        status = 'warning'
    
    return jsonify({
        'sensor_data': sensor_data,
        'health_score': health_score,
        'status': status,
        'anomalies': anomalies,
        'predictions': predictions,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/historical-data')
def get_historical_data():
    hours = request.args.get('hours', default=24, type=int)
    data = db.get_historical_data(hours)
    return jsonify(data)

@app.route('/api/diagnostics')
def get_diagnostics():
    sensor_data = simulator.generate_sensor_reading()
    dtc_codes = simulator.generate_dtc_codes(sensor_data)
    
    diagnostics = []
    for code in dtc_codes:
        diagnostics.append({
            'code': code['code'],
            'description': code['description'],
            'severity': code['severity'],
            'recommendation': code['recommendation']
        })
    
    return jsonify(diagnostics)

@app.route('/api/maintenance-predictions')
def get_maintenance_predictions():
    recent_data = db.get_historical_data(hours=168)
    
    if len(recent_data) < 10:
        sensor_data = simulator.generate_sensor_reading()
        for _ in range(10):
            db.log_sensor_data(sensor_data)
            sensor_data = simulator.generate_sensor_reading()
        recent_data = db.get_historical_data(hours=168)
    
    predictions = ai_model.advanced_maintenance_prediction(recent_data)
    
    return jsonify(predictions)

@app.route('/api/stats')
def get_stats():
    stats = db.get_statistics()
    return jsonify(stats)

@app.route('/api/reset-simulation')
def reset_simulation():
    simulator.reset()
    return jsonify({'status': 'success', 'message': 'Simulation reset'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7001, debug=False)
