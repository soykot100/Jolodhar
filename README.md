# JOLODHAR - Smart IoT-ML Drain Monitoring System

**Team Aphelion** | NASA Space Apps Challenge

JOLODHAR (জলধার) is a smart IoT-ML powered drainage monitoring system for Bangladesh. It combines real-time IoT sensor data, NASA POWER weather API, and Machine Learning (RandomForest) to predict drain blockage, flood risk, and road conditions — helping both the public and administrators make informed decisions.

## Features

### Public View (`/public`)
- **Live Map** — color-coded road/drain status (green=clear, yellow=caution, red=waterlogged)
- **Tomorrow Rain Forecast** — Google Weather-style "Will it rain tomorrow?" with probability
- **Current Weather** — temperature, humidity, precipitation, wind (NASA POWER API)
- **Road Conditions** — which roads are waterlogged vs safe to use right now
- **Smart Suggestions** — actionable advice based on current conditions
- **Notifications** — active alerts for the selected district
- **Hourly Forecast** — 24-hour breakdown for tomorrow
- **Bengali + English** — full language toggle

### Control Panel (`/control`) — Login Required
- **Dashboard** — system overview with live charts
- **Digital Twin** — drain network visualization with sensor readings
- **Sensors** — manage all IoT sensors with battery/signal status
- **Workers** — field worker management
- **Reports** — daily/weekly/monthly/custom reports with CSV export
- **ML Metrics** — full training metrics for judges:
  - Accuracy, Precision, Recall, F1, F2, R², RMSE, AUC-ROC
  - Confusion Matrix
  - Feature Importance chart
  - 5-fold Cross-Validation scores
  - Live Prediction Demo
- **Notifications** — all system alerts

## Tech Stack
- **Backend:** Flask 3.0 + Flask-SocketIO (WebSocket) + SQLite
- **ML:** scikit-learn RandomForestClassifier (11 features, 3 classes)
- **Weather:** NASA POWER API + Open-Meteo Forecast API
- **Frontend:** HTML/CSS/JS + Leaflet maps + Chart.js
- **Languages:** Bengali + English (full i18n)

## Quick Start (VS Code)

### Prerequisites
- Python 3.9 or higher
- pip (Python package installer)

### Step 1: Install dependencies
```bash
cd jolodhar
pip install -r requirements.txt
```

### Step 2: Train the ML model (first time only)
```bash
python ml/train_model.py
```
This creates:
- `ml/model.pkl` — trained RandomForest model
- `ml/scaler.pkl` — feature scaler
- `ml/metrics.json` — all training metrics
- `ml/feature_columns.json` — feature list
- `ml/training_dataset.csv` — training data reference

### Step 3: Run the application
```bash
python app.py
```

### Step 4: Open in browser
- **Public View:** http://localhost:5000/public
- **Control Panel Login:** http://localhost:5000/login
  - Username: `admin`
  - Password: `jolodhar2025`

## Project Structure
```
jolodhar/
├── app.py                    # Main Flask application
├── config.py                 # Configuration
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
├── .env.example              # Template for .env
├── ml/
│   ├── train_model.py        # ML training script
│   ├── predict.py            # Prediction service
│   ├── model.pkl             # Trained model (generated)
│   ├── scaler.pkl            # Feature scaler (generated)
│   ├── metrics.json          # Training metrics (generated)
│   └── feature_columns.json  # Feature list (generated)
├── services/
│   ├── nasa_power.py         # NASA POWER API client
│   ├── weather_forecast.py   # Weather forecast service
│   ├── i18n.py               # Bengali/English translations
│   └── database.py           # SQLite + demo data
├── data/
│   ├── districts.py          # 64 BD districts with GPS
│   └── jolodhar.db           # SQLite DB (auto-generated)
├── templates/
│   ├── base.html             # Base layout
│   ├── public.html           # Public dashboard
│   ├── control.html          # Control panel
│   ├── login.html            # Login page
│   ├── error.html            # Error page
│   └── partials/             # Control panel sections
│       ├── dashboard.html
│       ├── digital_twin.html
│       ├── sensors.html
│       ├── workers.html
│       ├── reports.html
│       ├── ml_metrics.html
│       └── notifications.html
├── static/
│   ├── css/style.css         # Premium sky blue/black theme
│   ├── js/
│   │   ├── i18n.js           # Language toggle
│   │   ├── app.js            # Common utilities + WebSocket
│   │   ├── public.js         # Public dashboard logic
│   │   └── control.js        # Control panel logic
│   └── images/
│       ├── logo.png          # Official JOLODHAR logo
│       ├── logo_icon.png     # Square icon version
│       ├── logo_small.png    # Small logo
│       └── favicon.png       # Favicon
├── scripts/
│   └── generate_logo.py      # Logo generator (optional)
├── logs/
│   └── jolodhar.log          # Application log
└── README.md                 # This file
```

## ML Model Details

### Features (11)
1. `rainfall` — Precipitation (mm/day) [NASA POWER]
2. `temperature` — Temperature at 2m (°C) [NASA POWER]
3. `humidity` — Relative humidity (%) [NASA POWER]
4. `wind_speed` — Wind speed (m/s) [NASA POWER]
5. `water_level` — Water level in drain (cm) [IoT sensor]
6. `flow_rate` — Flow rate (m³/s) [IoT sensor]
7. `drain_depth` — Drain depth (cm) [physical]
8. `drain_width` — Drain width (cm) [physical]
9. `population_density` — Population density (people/km²)
10. `last_maintenance_days` — Days since last cleaning
11. `debris_indicator` — Debris detection score 0-1 [IoT sensor]

### Classes (3)
- **0 = Normal** — drain operating normally
- **1 = Warning** — blockage risk developing
- **2 = Critical** — flood/blocked

### Training Results
- **Accuracy:** 89.17%
- **Precision (macro):** 89.30%
- **Recall (macro):** 83.90%
- **F1 Score (macro):** 86.29%
- **F2 Score (macro):** 84.79%
- **R²:** 71.71%
- **RMSE:** 0.3291
- **AUC-ROC:** 96.83%
- **5-fold CV:** 90.46% ± 0.78%

## API Endpoints

### Weather
- `GET /api/weather/current?lat=&lon=&lang=` — current weather
- `GET /api/weather/tomorrow?lat=&lon=&lang=` — tomorrow's forecast
- `GET /api/weather/district/<name>` — weather by district name
- `GET /api/weather/nasa-power?lat=&lon=&days=7` — raw NASA POWER data

### Data
- `GET /api/districts` — all 64 BD districts
- `GET /api/sensors` — all sensors
- `GET /api/sensors/<id>` — sensor detail with readings
- `GET /api/roads?district=` — road conditions (clear/caution/blocked)
- `GET /api/suggestions?district=` — smart recommendations
- `GET /api/notifications` — recent notifications
- `GET /api/routes` — route logs
- `GET /api/workers` — field workers
- `GET /api/incidents` — incidents
- `GET /api/dashboard/stats` — dashboard summary

### ML
- `GET /api/ml/metrics` — all training metrics
- `POST /api/ml/predict` — live prediction (JSON body with 11 features)
- `GET /api/ml/feature-importance` — feature importance list

### Language
- `POST /api/lang/<lang>` — set language (`en` or `bn`)

## Authentication
Control panel requires login. Default credentials:
- **Username:** `admin`
- **Password:** `jolodhar2025`

Change these in `.env` file:
```
ADMIN_USERNAME=your_username
ADMIN_PASSWORD=your_password
```

## Configuration
All settings are in `config.py` and can be overridden via `.env`:
- `PORT` — server port (default 5000)
- `DEBUG` — debug mode (default True)
- `ADMIN_USERNAME` / `ADMIN_PASSWORD` — login credentials
- `DEFAULT_DISTRICT` — default district (default Dhaka)
- `DEFAULT_LANGUAGE` — default language (`bn` or `en`)

## Data Sources
1. **NASA POWER API** — historical/recent weather data (precipitation, temperature, humidity, wind, pressure, cloud cover, solar radiation, dew point)
2. **Open-Meteo Forecast API** — tomorrow's forecast (free, no API key)
3. **Mendeley BD District Dataset** — Bangladesh district information
4. **IoT Sensors (simulated)** — water level, flow rate, debris indicator

## Theme
- **Primary:** Sky Blue (`#0EA5E9`)
- **Background:** Light Black / Slate (`#0F172A`)
- **Accent:** Cyan (`#06B6D4`)
- **Status colors:** Green (clear), Yellow (caution), Red (blocked)

## Troubleshooting

### Port already in use
Change the port in `.env`:
```
PORT=5001
```

### ML model not loaded
Run training:
```bash
python ml/train_model.py
```

### Database issues
Delete the database and restart (it auto-creates with demo data):
```bash
rm data/jolodhar.db
python app.py
```

### Weather API not working
- NASA POWER API may have rate limits — wait a few minutes
- Internet connection required
- The app falls back gracefully if APIs are unavailable

## License
MIT License — Team Aphelion, NASA Space Apps Challenge 2025.

## Credits
- **Team Aphelion** — Development
- **NASA POWER API** — Weather data
- **Open-Meteo** — Forecast data
- **OpenStreetMap** — Map tiles
