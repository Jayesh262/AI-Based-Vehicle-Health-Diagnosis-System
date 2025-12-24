import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pandas as pd

class VehicleHealthAI:
    def __init__(self):
        self.anomaly_detector = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.training_data = []
    
    def extract_features(self, sensor_data):
        features = [
            sensor_data['engine_temp'],
            sensor_data['oil_pressure'],
            sensor_data['battery_voltage'],
            sensor_data['tire_pressure']['front_left'],
            sensor_data['tire_pressure']['front_right'],
            sensor_data['tire_pressure']['rear_left'],
            sensor_data['tire_pressure']['rear_right'],
            sensor_data['rpm'],
            sensor_data['speed'],
            sensor_data['fuel_level'],
            sensor_data['coolant_level'],
            sensor_data['brake_fluid_level']
        ]
        return np.array(features).reshape(1, -1)
    
    def calculate_health_score(self, sensor_data):
        score = 100
        
        if sensor_data['engine_temp'] > 105:
            score -= 30
        elif sensor_data['engine_temp'] > 95:
            score -= 10
        
        if sensor_data['oil_pressure'] < 20:
            score -= 35
        elif sensor_data['oil_pressure'] < 30:
            score -= 15
        
        if sensor_data['battery_voltage'] < 11.5:
            score -= 25
        elif sensor_data['battery_voltage'] < 12.0:
            score -= 10
        
        for tire_pressure in sensor_data['tire_pressure'].values():
            if tire_pressure < 26:
                score -= 15
            elif tire_pressure < 28:
                score -= 5
        
        if sensor_data['coolant_level'] < 70:
            score -= 15
        elif sensor_data['coolant_level'] < 80:
            score -= 5
        
        if sensor_data['brake_fluid_level'] < 75:
            score -= 20
        elif sensor_data['brake_fluid_level'] < 85:
            score -= 8
        
        return max(0, min(100, score))
    
    def detect_anomalies(self, sensor_data):
        features = self.extract_features(sensor_data)
        
        self.training_data.append(features[0])
        if len(self.training_data) > 100:
            self.training_data.pop(0)
        
        anomalies = []
        
        if len(self.training_data) >= 10:
            if not self.is_trained or len(self.training_data) % 20 == 0:
                X_train = np.array(self.training_data)
                self.scaler.fit(X_train)
                X_scaled = self.scaler.transform(X_train)
                self.anomaly_detector.fit(X_scaled)
                self.is_trained = True
            
            X_scaled = self.scaler.transform(features)
            prediction = self.anomaly_detector.predict(X_scaled)
            anomaly_score = self.anomaly_detector.score_samples(X_scaled)[0]
            
            if prediction[0] == -1:
                anomalies.append({
                    'type': 'ML_ANOMALY',
                    'description': 'Unusual sensor pattern detected by AI model',
                    'severity': 'warning',
                    'confidence': round(abs(anomaly_score) * 100, 2)
                })
        
        if sensor_data['engine_temp'] > 110:
            anomalies.append({
                'type': 'CRITICAL_TEMP',
                'description': 'Critical engine temperature detected',
                'severity': 'critical',
                'confidence': 100
            })
        
        if sensor_data['oil_pressure'] < 15:
            anomalies.append({
                'type': 'CRITICAL_OIL',
                'description': 'Critically low oil pressure',
                'severity': 'critical',
                'confidence': 100
            })
        
        tire_pressures = list(sensor_data['tire_pressure'].values())
        avg_pressure = np.mean(tire_pressures)
        std_pressure = np.std(tire_pressures)
        
        if std_pressure > 3:
            anomalies.append({
                'type': 'TIRE_IMBALANCE',
                'description': 'Significant tire pressure imbalance detected',
                'severity': 'warning',
                'confidence': round(min(std_pressure * 20, 100), 2)
            })
        
        return anomalies
    
    def predict_maintenance(self, sensor_data):
        predictions = []
        
        oil_health = (sensor_data['oil_pressure'] - 20) / (50 - 20) * 100
        oil_health = max(0, min(100, oil_health))
        
        if oil_health < 60:
            days_until = int((oil_health / 100) * 30)
            predictions.append({
                'component': 'Oil Change',
                'days_until': max(1, days_until),
                'urgency': 'high' if days_until < 7 else 'medium',
                'confidence': round(100 - oil_health, 2)
            })
        
        battery_health = (sensor_data['battery_voltage'] - 11) / (13 - 11) * 100
        battery_health = max(0, min(100, battery_health))
        
        if battery_health < 70:
            days_until = int((battery_health / 100) * 60)
            predictions.append({
                'component': 'Battery Replacement',
                'days_until': max(1, days_until),
                'urgency': 'high' if days_until < 14 else 'medium',
                'confidence': round(100 - battery_health, 2)
            })
        
        coolant_health = sensor_data['coolant_level']
        if coolant_health < 85:
            days_until = int((coolant_health / 100) * 45)
            predictions.append({
                'component': 'Coolant Service',
                'days_until': max(1, days_until),
                'urgency': 'high' if coolant_health < 70 else 'medium',
                'confidence': round(100 - coolant_health, 2)
            })
        
        brake_health = sensor_data['brake_fluid_level']
        if brake_health < 90:
            days_until = int((brake_health / 100) * 40)
            predictions.append({
                'component': 'Brake System Check',
                'days_until': max(1, days_until),
                'urgency': 'high' if brake_health < 75 else 'medium',
                'confidence': round(100 - brake_health, 2)
            })
        
        if sensor_data.get('operating_hours', 0) > 500:
            predictions.append({
                'component': 'General Service',
                'days_until': 30,
                'urgency': 'low',
                'confidence': 75
            })
        
        return sorted(predictions, key=lambda x: x['days_until'])
    
    def advanced_maintenance_prediction(self, historical_data):
        if len(historical_data) < 10:
            return []
        
        df = pd.DataFrame(historical_data)
        
        predictions = []
        
        if 'engine_temp' in df.columns:
            temp_trend = np.polyfit(range(len(df)), df['engine_temp'], 1)[0]
            if temp_trend > 0.5:
                predictions.append({
                    'component': 'Cooling System',
                    'trend': 'increasing_temperature',
                    'prediction': 'Cooling system efficiency may be declining',
                    'recommendation': 'Schedule cooling system inspection',
                    'confidence': min(abs(temp_trend) * 50, 95)
                })
        
        if 'oil_pressure' in df.columns:
            oil_trend = np.polyfit(range(len(df)), df['oil_pressure'], 1)[0]
            if oil_trend < -0.3:
                predictions.append({
                    'component': 'Engine Oil',
                    'trend': 'decreasing_pressure',
                    'prediction': 'Oil pressure showing declining trend',
                    'recommendation': 'Check oil level and quality. May need oil change',
                    'confidence': min(abs(oil_trend) * 100, 90)
                })
        
        if 'battery_voltage' in df.columns:
            battery_trend = np.polyfit(range(len(df)), df['battery_voltage'], 1)[0]
            if battery_trend < -0.05:
                predictions.append({
                    'component': 'Battery',
                    'trend': 'voltage_decline',
                    'prediction': 'Battery voltage trending downward',
                    'recommendation': 'Battery may need replacement soon',
                    'confidence': min(abs(battery_trend) * 200, 85)
                })
        
        return predictions
