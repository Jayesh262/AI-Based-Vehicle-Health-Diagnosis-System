import sqlite3
from datetime import datetime, timedelta
import json

class Database:
    def __init__(self, db_name='vehicle_health.db'):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                engine_temp REAL,
                oil_pressure REAL,
                battery_voltage REAL,
                tire_pressure_fl REAL,
                tire_pressure_fr REAL,
                tire_pressure_rl REAL,
                tire_pressure_rr REAL,
                rpm REAL,
                speed REAL,
                fuel_level REAL,
                coolant_level REAL,
                brake_fluid_level REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_sensor_data(self, sensor_data):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sensor_logs (
                engine_temp, oil_pressure, battery_voltage,
                tire_pressure_fl, tire_pressure_fr, tire_pressure_rl, tire_pressure_rr,
                rpm, speed, fuel_level, coolant_level, brake_fluid_level
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
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
        ))
        
        conn.commit()
        conn.close()
    
    def get_historical_data(self, hours=24):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        time_threshold = datetime.now() - timedelta(hours=hours)
        
        cursor.execute('''
            SELECT * FROM sensor_logs
            WHERE timestamp > ?
            ORDER BY timestamp ASC
        ''', (time_threshold,))
        
        rows = cursor.fetchall()
        conn.close()
        
        data = []
        for row in rows:
            data.append({
                'timestamp': row['timestamp'],
                'engine_temp': row['engine_temp'],
                'oil_pressure': row['oil_pressure'],
                'battery_voltage': row['battery_voltage'],
                'tire_pressure': {
                    'front_left': row['tire_pressure_fl'],
                    'front_right': row['tire_pressure_fr'],
                    'rear_left': row['tire_pressure_rl'],
                    'rear_right': row['tire_pressure_rr']
                },
                'rpm': row['rpm'],
                'speed': row['speed'],
                'fuel_level': row['fuel_level'],
                'coolant_level': row['coolant_level'],
                'brake_fluid_level': row['brake_fluid_level']
            })
        
        return data
    
    def get_statistics(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as total FROM sensor_logs')
        total_readings = cursor.fetchone()['total']
        
        cursor.execute('''
            SELECT 
                AVG(engine_temp) as avg_engine_temp,
                AVG(oil_pressure) as avg_oil_pressure,
                AVG(battery_voltage) as avg_battery_voltage,
                AVG(rpm) as avg_rpm,
                AVG(speed) as avg_speed
            FROM sensor_logs
            WHERE timestamp > datetime('now', '-24 hours')
        ''')
        
        stats = cursor.fetchone()
        conn.close()
        
        return {
            'total_readings': total_readings,
            'avg_engine_temp': round(stats['avg_engine_temp'], 2) if stats['avg_engine_temp'] else 0,
            'avg_oil_pressure': round(stats['avg_oil_pressure'], 2) if stats['avg_oil_pressure'] else 0,
            'avg_battery_voltage': round(stats['avg_battery_voltage'], 2) if stats['avg_battery_voltage'] else 0,
            'avg_rpm': round(stats['avg_rpm'], 2) if stats['avg_rpm'] else 0,
            'avg_speed': round(stats['avg_speed'], 2) if stats['avg_speed'] else 0
        }
