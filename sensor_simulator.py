import random
import numpy as np
from datetime import datetime

class SensorSimulator:
    def __init__(self):
        self.operating_hours = 0
        self.degradation_factor = 0
        self.random_state = random.Random()
        self.np_random = np.random.RandomState()
    
    def reset(self):
        self.operating_hours = 0
        self.degradation_factor = 0
    
    def generate_sensor_reading(self):
        self.operating_hours += random.uniform(0.1, 0.5)
        self.degradation_factor = min(self.operating_hours / 10000, 0.3)
        
        base_engine_temp = 90
        engine_temp = base_engine_temp + random.uniform(-5, 15) + (self.degradation_factor * 20)
        
        base_oil_pressure = 45
        oil_pressure = base_oil_pressure + random.uniform(-5, 5) - (self.degradation_factor * 10)
        
        base_battery_voltage = 12.6
        battery_voltage = base_battery_voltage + random.uniform(-0.3, 0.3) - (self.degradation_factor * 1.5)
        
        base_tire_pressure = 32
        tire_pressures = {
            'front_left': base_tire_pressure + random.uniform(-2, 2),
            'front_right': base_tire_pressure + random.uniform(-2, 2),
            'rear_left': base_tire_pressure + random.uniform(-2, 2),
            'rear_right': base_tire_pressure + random.uniform(-2, 2)
        }
        
        rpm = random.uniform(700, 4000)
        speed = random.uniform(0, 80)
        fuel_level = random.uniform(20, 100)
        coolant_level = random.uniform(80, 100) - (self.degradation_factor * 20)
        brake_fluid_level = random.uniform(85, 100) - (self.degradation_factor * 15)
        
        if random.random() < 0.1:
            anomaly_type = random.choice(['overheat', 'low_oil', 'low_battery', 'low_tire'])
            if anomaly_type == 'overheat':
                engine_temp += random.uniform(10, 30)
            elif anomaly_type == 'low_oil':
                oil_pressure -= random.uniform(10, 20)
            elif anomaly_type == 'low_battery':
                battery_voltage -= random.uniform(1, 2)
            elif anomaly_type == 'low_tire':
                tire_key = random.choice(list(tire_pressures.keys()))
                tire_pressures[tire_key] -= random.uniform(5, 10)
        
        return {
            'engine_temp': round(engine_temp, 2),
            'oil_pressure': round(max(0, oil_pressure), 2),
            'battery_voltage': round(battery_voltage, 2),
            'tire_pressure': {k: round(max(0, v), 2) for k, v in tire_pressures.items()},
            'rpm': round(rpm, 2),
            'speed': round(speed, 2),
            'fuel_level': round(fuel_level, 2),
            'coolant_level': round(coolant_level, 2),
            'brake_fluid_level': round(brake_fluid_level, 2),
            'operating_hours': round(self.operating_hours, 2)
        }
    
    def generate_dtc_codes(self, sensor_data):
        codes = []
        
        if sensor_data['engine_temp'] > 105:
            codes.append({
                'code': 'P0217',
                'description': 'Engine Coolant Over Temperature',
                'severity': 'critical',
                'recommendation': 'Stop driving immediately. Check coolant level and radiator. Seek professional service.'
            })
        
        if sensor_data['oil_pressure'] < 20:
            codes.append({
                'code': 'P0524',
                'description': 'Engine Oil Pressure Too Low',
                'severity': 'critical',
                'recommendation': 'Stop engine immediately. Check oil level. Do not drive until resolved.'
            })
        
        if sensor_data['battery_voltage'] < 11.5:
            codes.append({
                'code': 'P0562',
                'description': 'System Voltage Low',
                'severity': 'warning',
                'recommendation': 'Check battery and alternator. Battery may need replacement soon.'
            })
        
        for position, pressure in sensor_data['tire_pressure'].items():
            if pressure < 26:
                codes.append({
                    'code': 'C0196',
                    'description': f'Tire Pressure Low - {position.replace("_", " ").title()}',
                    'severity': 'warning',
                    'recommendation': f'Inflate {position.replace("_", " ")} tire to recommended pressure (32 PSI).'
                })
        
        if sensor_data['coolant_level'] < 70:
            codes.append({
                'code': 'P0118',
                'description': 'Coolant Level Low',
                'severity': 'warning',
                'recommendation': 'Top up coolant reservoir. Check for leaks.'
            })
        
        if sensor_data['brake_fluid_level'] < 75:
            codes.append({
                'code': 'C1288',
                'description': 'Brake Fluid Level Low',
                'severity': 'warning',
                'recommendation': 'Check brake fluid level and brake pad wear. Service brakes if needed.'
            })
        
        if sensor_data['fuel_level'] < 15:
            codes.append({
                'code': 'P0461',
                'description': 'Fuel Level Sensor Low',
                'severity': 'info',
                'recommendation': 'Refuel soon to avoid running empty.'
            })
        
        return codes
