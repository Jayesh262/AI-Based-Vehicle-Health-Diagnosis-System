let trendsChart = null;
let updateInterval = null;

const chartColors = {
    engineTemp: 'rgb(239, 68, 68)',
    oilPressure: 'rgb(59, 130, 246)',
    batteryVoltage: 'rgb(34, 197, 94)',
    speed: 'rgb(168, 85, 247)'
};

function initChart() {
    const ctx = document.getElementById('trendsChart').getContext('2d');
    
    trendsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Engine Temp (°C)',
                    data: [],
                    borderColor: chartColors.engineTemp,
                    backgroundColor: chartColors.engineTemp + '20',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Oil Pressure (PSI)',
                    data: [],
                    borderColor: chartColors.oilPressure,
                    backgroundColor: chartColors.oilPressure + '20',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Battery (V × 10)',
                    data: [],
                    borderColor: chartColors.batteryVoltage,
                    backgroundColor: chartColors.batteryVoltage + '20',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }
            }
        }
    });
}

function updateChart(sensorData) {
    if (!trendsChart) return;
    
    const now = new Date().toLocaleTimeString();
    
    if (trendsChart.data.labels.length > 20) {
        trendsChart.data.labels.shift();
        trendsChart.data.datasets.forEach(dataset => dataset.data.shift());
    }
    
    trendsChart.data.labels.push(now);
    trendsChart.data.datasets[0].data.push(sensorData.engine_temp);
    trendsChart.data.datasets[1].data.push(sensorData.oil_pressure);
    trendsChart.data.datasets[2].data.push(sensorData.battery_voltage * 10);
    
    trendsChart.update('none');
}

function updateDashboard(data) {
    const sensor = data.sensor_data;
    
    document.getElementById('health-score').textContent = Math.round(data.health_score);
    
    const statusElement = document.getElementById('health-status');
    statusElement.textContent = data.status.toUpperCase();
    statusElement.className = 'health-status text-' + data.status;
    
    document.getElementById('engine-temp').textContent = sensor.engine_temp.toFixed(1);
    updateProgressBar('engine-temp-bar', sensor.engine_temp, 40, 120, true);
    
    document.getElementById('oil-pressure').textContent = sensor.oil_pressure.toFixed(1);
    updateProgressBar('oil-pressure-bar', sensor.oil_pressure, 0, 60);
    
    document.getElementById('battery-voltage').textContent = sensor.battery_voltage.toFixed(2);
    updateProgressBar('battery-bar', sensor.battery_voltage, 11, 13);
    
    document.getElementById('speed').textContent = sensor.speed.toFixed(0);
    updateProgressBar('speed-bar', sensor.speed, 0, 120);
    
    document.getElementById('tire-fl').textContent = sensor.tire_pressure.front_left.toFixed(1);
    document.getElementById('tire-fr').textContent = sensor.tire_pressure.front_right.toFixed(1);
    document.getElementById('tire-rl').textContent = sensor.tire_pressure.rear_left.toFixed(1);
    document.getElementById('tire-rr').textContent = sensor.tire_pressure.rear_right.toFixed(1);
    
    document.getElementById('fuel-level').textContent = sensor.fuel_level.toFixed(0);
    document.getElementById('rpm').textContent = sensor.rpm.toFixed(0);
    
    updateChart(sensor);
    
    updateAlerts(data.anomalies);
    
    const updateTime = new Date(data.timestamp).toLocaleString();
    document.getElementById('last-update').textContent = updateTime;
}

function updateProgressBar(elementId, value, min, max, inverse = false) {
    const element = document.getElementById(elementId);
    const percentage = ((value - min) / (max - min)) * 100;
    const clampedPercentage = Math.max(0, Math.min(100, percentage));
    
    element.style.width = clampedPercentage + '%';
    
    let colorClass = 'bg-success';
    if (inverse) {
        if (clampedPercentage > 80) colorClass = 'bg-danger';
        else if (clampedPercentage > 60) colorClass = 'bg-warning';
    } else {
        if (clampedPercentage < 30) colorClass = 'bg-danger';
        else if (clampedPercentage < 60) colorClass = 'bg-warning';
    }
    
    element.className = 'progress-bar ' + colorClass;
}

function updateAlerts(anomalies) {
    const container = document.getElementById('alerts-container');
    
    if (!anomalies || anomalies.length === 0) {
        container.innerHTML = '<p class="text-muted text-center mb-0">No active alerts</p>';
        return;
    }
    
    let html = '';
    anomalies.forEach(alert => {
        const severityClass = alert.severity === 'critical' ? 'alert-critical' : 
                            alert.severity === 'warning' ? 'alert-warning' : 'alert-info';
        html += `
            <div class="alert-item ${severityClass}">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <strong>${alert.type.replace(/_/g, ' ')}</strong>
                        <p class="mb-0 mt-1">${alert.description}</p>
                    </div>
                    <span class="badge bg-dark">${alert.confidence}%</span>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function updatePredictions(predictions) {
    const container = document.getElementById('predictions-container');
    
    if (!predictions || predictions.length === 0) {
        container.innerHTML = '<p class="text-muted text-center mb-0">No maintenance needed</p>';
        return;
    }
    
    let html = '';
    predictions.forEach(pred => {
        html += `
            <div class="prediction-item urgency-${pred.urgency}">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <strong>${pred.component}</strong>
                        <p class="mb-0 mt-1 text-muted">
                            <small>In ${pred.days_until} days - Urgency: ${pred.urgency}</small>
                        </p>
                    </div>
                    <span class="badge bg-primary">${pred.confidence}%</span>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function updateDTC(dtcCodes) {
    const container = document.getElementById('dtc-container');
    
    if (!dtcCodes || dtcCodes.length === 0) {
        container.innerHTML = '<p class="text-muted text-center mb-0">No trouble codes detected</p>';
        return;
    }
    
    let html = '';
    dtcCodes.forEach(code => {
        const severityBadge = code.severity === 'critical' ? 'bg-danger' : 
                            code.severity === 'warning' ? 'bg-warning' : 'bg-info';
        html += `
            <div class="dtc-item">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <span class="dtc-code">${code.code}</span>
                    <span class="badge ${severityBadge}">${code.severity}</span>
                </div>
                <p class="mb-2"><strong>${code.description}</strong></p>
                <p class="mb-0 text-muted"><small><i class="fas fa-wrench"></i> ${code.recommendation}</small></p>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

async function fetchCurrentStatus() {
    try {
        const response = await fetch('/api/current-status');
        const data = await response.json();
        updateDashboard(data);
    } catch (error) {
        console.error('Error fetching status:', error);
        document.getElementById('status-badge').textContent = 'Disconnected';
        document.getElementById('status-badge').className = 'badge bg-danger';
    }
}

async function fetchPredictions() {
    try {
        const response = await fetch('/api/maintenance-predictions');
        const predictions = await response.json();
        updatePredictions(predictions);
    } catch (error) {
        console.error('Error fetching predictions:', error);
    }
}

async function fetchDTC() {
    try {
        const response = await fetch('/api/diagnostics');
        const dtcCodes = await response.json();
        updateDTC(dtcCodes);
    } catch (error) {
        console.error('Error fetching DTC:', error);
    }
}

function refreshData() {
    fetchCurrentStatus();
    fetchPredictions();
    fetchDTC();
}

async function resetSimulation() {
    try {
        await fetch('/api/reset-simulation');
        refreshData();
        alert('Simulation has been reset!');
    } catch (error) {
        console.error('Error resetting simulation:', error);
        alert('Failed to reset simulation');
    }
}

function startAutoUpdate() {
    updateInterval = setInterval(() => {
        fetchCurrentStatus();
    }, 3000);
    
    setInterval(() => {
        fetchPredictions();
        fetchDTC();
    }, 10000);
}

document.addEventListener('DOMContentLoaded', () => {
    initChart();
    refreshData();
    startAutoUpdate();
});
