# Vehicle Health Monitoring System

## Overview
An AI-based Vehicle Health Monitoring System built with Flask that provides real-time vehicle diagnostics, anomaly detection, and predictive maintenance alerts. The system uses machine learning (scikit-learn) to analyze sensor data and predict potential issues before they become critical.

## Current State
- **Status**: Fully functional MVP
- **Framework**: Flask (Python)
- **Database**: SQLite for sensor data logging
- **AI/ML**: scikit-learn Isolation Forest for anomaly detection
- **Frontend**: Bootstrap 5, Chart.js for visualizations


## Project Architecture

### Backend Structure
- `app.py` - Main Flask application with API routes
- `database.py` - SQLite database management for sensor logs
- `sensor_simulator.py` - Realistic vehicle sensor data generator
- `ml_models.py` - AI/ML models for health analysis and predictions

### Frontend Structure
- `templates/index.html` - Main dashboard interface
- `static/css/style.css` - Automotive-themed styling
- `static/js/app.js` - Real-time data updates and Chart.js visualizations

### Key Features
1. **Real-time Monitoring**: Engine temp, oil pressure, battery voltage, tire pressure, RPM, speed
2. **AI Anomaly Detection**: Machine learning identifies unusual patterns
3. **Health Scoring**: 0-100 score with color-coded status (healthy/warning/critical)
4. **Predictive Maintenance**: Forecasts component failures before they occur
5. **DTC System**: Diagnostic trouble codes with recommendations
6. **Historical Trends**: Chart.js visualizations of sensor data over time
7. **Auto-refresh**: Dashboard updates every 3 seconds

## API Endpoints
- `GET /` - Main dashboard
- `GET /api/current-status` - Current sensor readings and health score
- `GET /api/historical-data?hours=24` - Historical sensor data
- `GET /api/diagnostics` - Diagnostic trouble codes
- `GET /api/maintenance-predictions` - Predictive maintenance alerts
- `GET /api/stats` - System statistics
- `GET /api/reset-simulation` - Reset simulation data

## Database Schema
**sensor_logs table**:
- Engine temperature, oil pressure, battery voltage
- Tire pressures (all 4 tires)
- RPM, speed, fuel level
- Coolant and brake fluid levels
- Timestamp for trend analysis

## Dependencies
- Flask - Web framework
- scikit-learn - Machine learning models
- pandas - Data processing
- NumPy - Numerical computations
- Flask-CORS - API cross-origin support

## User Preferences
None set yet.

updated by Jayesh
