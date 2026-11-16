"""
JOLODHAR - Smart IoT-ML Drain Monitoring System
Configuration file
Team Aphelion - NASA Space Apps Challenge
"""

import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration for JOLODHAR"""

    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "jolodhar-aphelion-nasa-2025-secret")
    DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() == "true"
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", 5000))

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'data', 'jolodhar.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Auth
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "jolodhar2025")
    SESSION_TIMEOUT = 3600  # 1 hour

    # NASA POWER API
    NASA_POWER_BASE = "https://power.larc.nasa.gov/api/temporal"
    NASA_POWER_TIMEOUT = 30

    # Open-Meteo Forecast API (free, no key — used for tomorrow's rain forecast)
    OPEN_METEO_BASE = "https://api.open-meteo.com/v1/forecast"
    OPEN_METEO_TIMEOUT = 20

    # Default location: Dhaka, Bangladesh
    DEFAULT_LAT = 23.8103
    DEFAULT_LON = 90.4125
    DEFAULT_DISTRICT = "Dhaka"

    # ML Model paths
    MODEL_PATH = os.path.join(BASE_DIR, "ml", "model.pkl")
    SCALER_PATH = os.path.join(BASE_DIR, "ml", "scaler.pkl")
    METRICS_PATH = os.path.join(BASE_DIR, "ml", "metrics.json")
    FEATURE_COLUMNS_PATH = os.path.join(BASE_DIR, "ml", "feature_columns.json")

    # WebSocket
    SOCKETIO_ASYNC_MODE = "eventlet"

    # Theme
    THEME_PRIMARY = "#0EA5E9"  # sky blue
    THEME_DARK = "#0F172A"  # light black / slate
    THEME_ACCENT = "#38BDF8"

    # Languages
    LANGUAGES = ["en", "bn"]
    DEFAULT_LANGUAGE = "bn"

    # Notification refresh interval (seconds)
    NOTIFICATION_REFRESH = 60

    # WebSocket update interval (seconds)
    WS_UPDATE_INTERVAL = 5


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
