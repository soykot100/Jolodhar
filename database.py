"""
JOLODHAR - Database Models + Demo Data Generator
SQLite database for sensors, workers, notifications, routes, incidents
Auto-creates tables and seeds demo data on first run
"""

import os
import sqlite3
import json
import logging
import random
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "jolodhar.db")


def get_db():
    """Get SQLite connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    c = conn.cursor()

    # Sensors table
    c.execute("""
        CREATE TABLE IF NOT EXISTS sensors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_id TEXT UNIQUE NOT NULL,
            district TEXT NOT NULL,
            location_name TEXT,
            lat REAL,
            lon REAL,
            sensor_type TEXT DEFAULT 'drain_level',
            status TEXT DEFAULT 'online',
            battery INTEGER DEFAULT 100,
            signal INTEGER DEFAULT 90,
            last_reading REAL DEFAULT 0,
            last_updated TEXT,
            installed_date TEXT,
            drain_depth REAL DEFAULT 150,
            drain_width REAL DEFAULT 80
        )
    """)

    # Workers table
    c.execute("""
        CREATE TABLE IF NOT EXISTS workers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            phone TEXT,
            zone TEXT,
            status TEXT DEFAULT 'available',
            shift TEXT DEFAULT 'morning',
            assigned_tasks INTEGER DEFAULT 0,
            rating REAL DEFAULT 4.5,
            joined_date TEXT
        )
    """)

    # Notifications table
    c.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            title TEXT,
            message TEXT,
            severity TEXT DEFAULT 'info',
            district TEXT,
            sensor_id TEXT,
            timestamp TEXT,
            is_read INTEGER DEFAULT 0,
            is_resolved INTEGER DEFAULT 0
        )
    """)

    # Route logs table
    c.execute("""
        CREATE TABLE IF NOT EXISTS route_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id TEXT,
            district TEXT,
            from_location TEXT,
            to_location TEXT,
            distance_km REAL,
            duration_min INTEGER,
            purpose TEXT,
            status TEXT DEFAULT 'completed',
            timestamp TEXT
        )
    """)

    # Incidents table
    c.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_type TEXT,
            district TEXT,
            sensor_id TEXT,
            severity TEXT,
            status TEXT DEFAULT 'open',
            reported_at TEXT,
            resolved_at TEXT,
            assigned_worker TEXT,
            description TEXT
        )
    """)

    # Sensor readings table (for historical charts)
    c.execute("""
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_id TEXT,
            water_level REAL,
            flow_rate REAL,
            debris_indicator REAL,
            rainfall REAL,
            temperature REAL,
            humidity REAL,
            prediction INTEGER,
            timestamp TEXT
        )
    """)

    # Settings table
    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    conn.commit()
    conn.close()
    logger.info("Database initialized")


def seed_demo_data():
    """Seed demo data if tables are empty"""
    conn = get_db()
    c = conn.cursor()

    # Check if already seeded
    c.execute("SELECT COUNT(*) as cnt FROM sensors")
    if c.fetchone()["cnt"] > 0:
        conn.close()
        return

    logger.info("Seeding demo data...")
    from data.districts import DISTRICTS

    # Seed sensors (3 per major district)
    sensor_count = 0
    major_districts = DISTRICTS[:20]  # top 20 districts
    for d in major_districts:
        for i in range(1, 4):  # 3 sensors per district
            sensor_id = f"JLD-{d['name'][:3].upper()}-{i:03d}"
            water_level = round(random.uniform(20, 130), 1)
            c.execute("""
                INSERT OR IGNORE INTO sensors (sensor_id, district, location_name, lat, lon, sensor_type,
                    status, battery, signal, last_reading, last_updated, installed_date,
                    drain_depth, drain_width)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sensor_id,
                d["name"],
                f"{d['name']} Zone {i}",
                d["lat"] + random.uniform(-0.05, 0.05),
                d["lon"] + random.uniform(-0.05, 0.05),
                random.choice(["drain_level", "flow_rate", "debris"]),
                random.choices(["online", "online", "online", "offline"], k=1)[0],
                random.randint(45, 100),
                random.randint(60, 100),
                water_level,
                datetime.now().isoformat(),
                (datetime.now() - timedelta(days=random.randint(30, 400))).isoformat(),
                round(random.uniform(80, 200), 1),
                round(random.uniform(40, 120), 1),
            ))
            sensor_count += 1
    logger.info(f"Seeded {sensor_count} sensors")

    # Seed workers
    worker_names_bn = [
        ("কামরুল হাসান", "Kamrul Hasan"),
        ("রফিকুল ইসলাম", "Rafiqul Islam"),
        ("আব্দুল করিম", "Abdul Karim"),
        ("নাসির উদ্দিন", "Nasir Uddin"),
        ("মোঃ আলম", "Md. Alam"),
        ("শাহানা বেগম", "Shahana Begum"),
        ("ফারুক আহমেদ", "Faruk Ahmed"),
        ("জাহাঙ্গীর আলম", "Jahangir Alam"),
        ("মমতাজ বেগম", "Momtaz Begum"),
        ("সালমা আক্তার", "Salma Akter"),
        ("নাদিম রহমান", "Nadim Rahman"),
        ("হাবিব মিয়া", "Habib Miah"),
    ]
    for i, (bn, en) in enumerate(worker_names_bn, 1):
        district = random.choice(DISTRICTS)
        worker_id = f"WKR-{i:03d}"
        c.execute("""
            INSERT OR IGNORE INTO workers (worker_id, name, phone, zone, status, shift, assigned_tasks, rating, joined_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            worker_id,
            en,
            f"+8801{random.randint(700, 799)}{random.randint(100000, 999999)}",
            district["name"],
            random.choices(["available", "on_task", "off_duty"], weights=[5, 3, 2], k=1)[0],
            random.choice(["morning", "evening", "night"]),
            random.randint(0, 5),
            round(random.uniform(3.5, 5.0), 1),
            (datetime.now() - timedelta(days=random.randint(60, 800))).isoformat(),
        ))
    logger.info(f"Seeded {len(worker_names_bn)} workers")

    # Seed notifications (recent ones)
    notif_types = [
        ("blockage", "Drain Blockage Alert", "Water level exceeded threshold", "critical"),
        ("flood", "Flood Risk Warning", "Heavy rainfall predicted", "critical"),
        ("rain", "Heavy Rain Alert", "60mm+ rainfall expected tomorrow", "warning"),
        ("sensor_offline", "Sensor Offline", "Sensor stopped responding", "warning"),
        ("maintenance", "Maintenance Required", "Cleaning overdue 90+ days", "info"),
        ("resolved", "Issue Resolved", "Blockage cleared successfully", "info"),
    ]
    for i in range(15):
        ntype, title, msg, sev = random.choice(notif_types)
        district = random.choice(DISTRICTS[:20])
        c.execute("""
            INSERT OR IGNORE INTO notifications (type, title, message, severity, district, sensor_id, timestamp, is_read, is_resolved)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ntype, title, msg, sev, district["name"],
            f"JLD-{district['name'][:3].upper()}-{random.randint(1,3):03d}",
            (datetime.now() - timedelta(hours=random.randint(1, 72))).isoformat(),
            random.randint(0, 1),
            1 if ntype == "resolved" else random.randint(0, 1),
        ))
    logger.info("Seeded 15 notifications")

    # Seed route logs
    purposes = ["inspection", "cleaning", "emergency", "maintenance", "monitoring"]
    for i in range(20):
        district = random.choice(DISTRICTS[:15])
        worker = c.execute("SELECT worker_id FROM workers ORDER BY RANDOM() LIMIT 1").fetchone()
        c.execute("""
            INSERT OR IGNORE INTO route_logs (worker_id, district, from_location, to_location, distance_km, duration_min, purpose, status, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            worker["worker_id"] if worker else "WKR-001",
            district["name"],
            f"{district['name']} Office",
            f"{district['name']} Zone {random.randint(1,5)}",
            round(random.uniform(1, 25), 1),
            random.randint(15, 180),
            random.choice(purposes),
            random.choice(["completed", "completed", "in_progress"]),
            (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat(),
        ))
    logger.info("Seeded 20 route logs")

    # Seed incidents
    incident_types = ["blockage", "flood", "overflow", "structural", "debris"]
    severities = ["low", "medium", "high", "critical"]
    for i in range(10):
        district = random.choice(DISTRICTS[:15])
        c.execute("""
            INSERT OR IGNORE INTO incidents (incident_type, district, sensor_id, severity, status, reported_at, assigned_worker, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            random.choice(incident_types),
            district["name"],
            f"JLD-{district['name'][:3].upper()}-{random.randint(1,3):03d}",
            random.choice(severities),
            random.choice(["open", "assigned", "resolved"]),
            (datetime.now() - timedelta(hours=random.randint(1, 120))).isoformat(),
            f"WKR-{random.randint(1,12):03d}",
            "Reported by IoT sensor monitoring system.",
        ))
    logger.info("Seeded 10 incidents")

    # Seed sensor readings (historical)
    for sensor_row in c.execute("SELECT sensor_id FROM sensors LIMIT 30").fetchall():
        sid = sensor_row["sensor_id"]
        for h in range(24):
            ts = (datetime.now() - timedelta(hours=h)).isoformat()
            c.execute("""
                INSERT OR IGNORE INTO sensor_readings (sensor_id, water_level, flow_rate, debris_indicator, rainfall, temperature, humidity, prediction, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sid,
                round(random.uniform(20, 130), 1),
                round(random.uniform(0.1, 3.5), 2),
                round(random.uniform(0.05, 0.8), 2),
                round(random.uniform(0, 50), 1),
                round(random.uniform(15, 35), 1),
                round(random.uniform(40, 90), 1),
                random.choice([0, 0, 0, 1, 1, 2]),
                ts,
            ))
    logger.info("Seeded 720 sensor readings")

    # Seed settings
    settings = {
        "system_name": "JOLODHAR",
        "system_version": "1.0.0",
        "team_name": "Team Aphelion",
        "default_district": "Dhaka",
        "default_language": "bn",
        "nasa_power_enabled": "true",
        "weather_forecast_enabled": "true",
        "ml_model_loaded": "true",
        "last_backup": datetime.now().isoformat(),
    }
    for k, v in settings.items():
        c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, v))

    conn.commit()
    conn.close()
    logger.info("Demo data seeding complete!")


if __name__ == "__main__":
    init_db()
    seed_demo_data()
    print(f"Database ready at: {DB_PATH}")
