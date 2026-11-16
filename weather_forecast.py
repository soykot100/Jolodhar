"""
JOLODHAR - Weather Forecast Service
Combines NASA POWER (historical/current) + Open-Meteo (forecast) for tomorrow's rain prediction
Provides Google Weather-style "Will it rain tomorrow?" feature
"""

import requests
import logging
from datetime import datetime, timedelta

from services.nasa_power import nasa_power_service

logger = logging.getLogger(__name__)


class WeatherForecastService:
    """Weather forecast service for JOLODHAR"""

    OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, timeout=20):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "JOLODHAR/1.0 (Team Aphelion)"
        })

    def _fetch_open_meteo_forecast(self, lat, lon, days=3):
        """Fetch forecast from Open-Meteo (free, no API key needed)"""
        params = {
            "latitude": round(float(lat), 4),
            "longitude": round(float(lon), 4),
            "daily": ",".join([
                "weather_code",
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "precipitation_probability_max",
                "precipitation_hours",
                "wind_speed_10m_max",
                "relative_humidity_2m_max",
                "relative_humidity_2m_min",
                "cloud_cover_mean",
                "sunrise",
                "sunset",
                "uv_index_max",
                "pressure_msl_mean",
            ]),
            "hourly": ",".join([
                "precipitation",
                "precipitation_probability",
                "temperature_2m",
                "relative_humidity_2m",
                "cloud_cover",
                "wind_speed_10m",
            ]),
            "current": ",".join([
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation",
                "cloud_cover",
                "wind_speed_10m",
                "pressure_msl",
            ]),
            "timezone": "Asia/Dhaka",
            "forecast_days": days,
        }

        try:
            resp = self.session.get(self.OPEN_METEO_URL, params=params, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Open-Meteo API error: {e}")
            return None

    @staticmethod
    def _weather_code_to_text(code, lang="bn"):
        """WMO weather code -> human readable text"""
        codes = {
            0: ("Clear Sky", "পরিষ্কার আকাশ"),
            1: ("Mainly Clear", "অধিকাংশ পরিষ্কার"),
            2: ("Partly Cloudy", "আংশিক মেঘাচ্ছন্ন"),
            3: ("Overcast", "পুরোপুরি মেঘাচ্ছন্ন"),
            45: ("Foggy", "কুয়াশাচ্ছন্ন"),
            48: ("Depositing Rime Fog", "কুয়াশা"),
            51: ("Light Drizzle", "হালকা গুঁড়ি বৃষ্টি"),
            53: ("Moderate Drizzle", "মাঝারি গুঁড়ি বৃষ্টি"),
            55: ("Dense Drizzle", "ঘন গুঁড়ি বৃষ্টি"),
            61: ("Slight Rain", "হালকা বৃষ্টি"),
            63: ("Moderate Rain", "মাঝারি বৃষ্টি"),
            65: ("Heavy Rain", "ভারী বৃষ্টি"),
            66: ("Freezing Light Rain", "হিম বৃষ্টি"),
            67: ("Freezing Heavy Rain", "ভারী হিম বৃষ্টি"),
            71: ("Slight Snow", "হালকা তুষার"),
            73: ("Moderate Snow", "মাঝারি তুষার"),
            75: ("Heavy Snow", "ভারী তুষার"),
            77: ("Snow Grains", "তুষারপাত"),
            80: ("Slight Rain Showers", "হালকা ঝুম বৃষ্টি"),
            81: ("Moderate Rain Showers", "মাঝারি ঝুম বৃষ্টি"),
            82: ("Violent Rain Showers", "ভারী ঝুম বৃষ্টি"),
            85: ("Slight Snow Showers", "হালকা তুষার ঝুম"),
            86: ("Heavy Snow Showers", "ভারী তুষার ঝুম"),
            95: ("Thunderstorm", "বজ্রবৃষ্টি"),
            96: ("Thunderstorm with Hail", "বজ্রবৃষ্টি সহ শিলা"),
            99: ("Severe Thunderstorm", "ভয়াবহ বজ্রবৃষ্টি"),
        }
        en, bn = codes.get(code, ("Unknown", "অজানা"))
        return bn if lang == "bn" else en

    def _parse_hourly_forecast(self, data, target_date):
        """Parse hourly forecast for a specific date (tomorrow)"""
        if not data or "hourly" not in data:
            return []

        hourly = data["hourly"]
        times = hourly.get("time", [])
        precip_prob = hourly.get("precipitation_probability", [])
        precip = hourly.get("precipitation", [])
        temp = hourly.get("temperature_2m", [])
        humidity = hourly.get("relative_humidity_2m", [])
        cloud = hourly.get("cloud_cover", [])
        wind = hourly.get("wind_speed_10m", [])

        result = []
        for i, t in enumerate(times):
            if not t.startswith(target_date):
                continue
            result.append({
                "hour": t.split("T")[1] if "T" in t else t,
                "precipitation_probability": precip_prob[i] if i < len(precip_prob) else None,
                "precipitation": round(precip[i], 2) if i < len(precip) and precip[i] is not None else 0,
                "temperature": round(temp[i], 1) if i < len(temp) and temp[i] is not None else None,
                "humidity": humidity[i] if i < len(humidity) else None,
                "cloud_cover": cloud[i] if i < len(cloud) else None,
                "wind_speed": round(wind[i], 1) if i < len(wind) and wind[i] is not None else None,
            })
        return result

    def get_tomorrow_forecast(self, lat, lon, lang="bn"):
        """
        Get tomorrow's forecast with rain probability (Google Weather style)
        Returns dict with rain_probability, weather_text, hourly breakdown
        """
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")

        data = self._fetch_open_meteo_forecast(lat, lon, days=3)
        if not data:
            return None

        daily = data.get("daily", {})
        times = daily.get("time", [])

        # Find tomorrow's index
        tomorrow_idx = None
        for i, t in enumerate(times):
            if t == tomorrow:
                tomorrow_idx = i
                break

        if tomorrow_idx is None:
            return None

        weather_code = daily.get("weather_code", [])[tomorrow_idx]
        temp_max = daily.get("temperature_2m_max", [])[tomorrow_idx]
        temp_min = daily.get("temperature_2m_min", [])[tomorrow_idx]
        precip_sum = daily.get("precipitation_sum", [])[tomorrow_idx]
        precip_prob_max = daily.get("precipitation_probability_max", [])[tomorrow_idx] if "precipitation_probability_max" in daily else None
        precip_hours = daily.get("precipitation_hours", [])[tomorrow_idx] if "precipitation_hours" in daily else 0
        wind_max = daily.get("wind_speed_10m_max", [])[tomorrow_idx]
        humidity_max = daily.get("relative_humidity_2m_max", [])[tomorrow_idx] if "relative_humidity_2m_max" in daily else None
        cloud_mean = daily.get("cloud_cover_mean", [])[tomorrow_idx] if "cloud_cover_mean" in daily else None
        sunrise = daily.get("sunrise", [])[tomorrow_idx] if "sunrise" in daily else None
        sunset = daily.get("sunset", [])[tomorrow_idx] if "sunset" in daily else None
        uv_index = daily.get("uv_index_max", [])[tomorrow_idx] if "uv_index_max" in daily else None
        pressure = daily.get("pressure_msl_mean", [])[tomorrow_idx] if "pressure_msl_mean" in daily else None

        # Compute rain probability
        rain_prob = precip_prob_max if precip_prob_max is not None else 0
        if precip_prob_max is None and precip_sum > 0:
            rain_prob = 70  # fallback if prob missing

        # Decision: will it rain?
        will_rain = rain_prob >= 50 or precip_sum >= 1.0
        rain_text = (
            f"হ্যাঁ, বৃষ্টির সম্ভাবনা ({int(rain_prob)}%)" if lang == "bn"
            else f"Yes, rain expected ({int(rain_prob)}%)"
        ) if will_rain else (
            "না, বৃষ্টি হওয়ার সম্ভাবনা কম" if lang == "bn"
            else "No, low rain probability"
        )

        # Hourly breakdown for tomorrow
        hourly = self._parse_hourly_forecast(data, tomorrow)

        # Get today's summary too (for comparison)
        today_idx = 0
        today_summary = {
            "weather_code": daily.get("weather_code", [])[today_idx],
            "weather_text": self._weather_code_to_text(daily.get("weather_code", [])[today_idx], lang),
            "temp_max": round(daily.get("temperature_2m_max", [])[today_idx], 1),
            "temp_min": round(daily.get("temperature_2m_min", [])[today_idx], 1),
            "precip_sum": round(daily.get("precipitation_sum", [])[today_idx], 2),
        }

        # Try to enrich with NASA POWER current data
        nasa_summary = nasa_power_service.get_current_summary(lat, lon)

        return {
            "date": tomorrow,
            "today": today,
            "will_rain": will_rain,
            "rain_probability": int(rain_prob) if rain_prob else 0,
            "rain_text": rain_text,
            "weather_code": weather_code,
            "weather_text": self._weather_code_to_text(weather_code, lang),
            "temp_max": round(temp_max, 1) if temp_max is not None else None,
            "temp_min": round(temp_min, 1) if temp_min is not None else None,
            "precipitation_sum": round(precip_sum, 2) if precip_sum is not None else 0,
            "precipitation_hours": precip_hours,
            "wind_speed_max": round(wind_max, 1) if wind_max is not None else None,
            "humidity_max": humidity_max,
            "cloud_cover": cloud_mean,
            "uv_index": round(uv_index, 1) if uv_index is not None else None,
            "pressure": round(pressure, 1) if pressure is not None else None,
            "sunrise": sunrise.split("T")[1] if sunrise and "T" in sunrise else sunrise,
            "sunset": sunset.split("T")[1] if sunset and "T" in sunset else sunset,
            "hourly": hourly,
            "today_summary": today_summary,
            "nasa_power_data": nasa_summary,
            "data_sources": ["NASA POWER API", "Open-Meteo Forecast"],
            "timestamp": datetime.now().isoformat(),
        }

    def get_current_weather(self, lat, lon, lang="bn"):
        """Get current weather snapshot"""
        data = self._fetch_open_meteo_forecast(lat, lon, days=1)
        if not data or "current" not in data:
            return None

        current = data["current"]
        daily = data.get("daily", {})

        # Get today's weather code from daily
        today_weather_code = daily.get("weather_code", [None])[0]
        sunrise = daily.get("sunrise", [None])[0]
        sunset = daily.get("sunset", [None])[0]
        uv_index = daily.get("uv_index_max", [None])[0]

        return {
            "temperature": round(current.get("temperature_2m", 0), 1),
            "humidity": current.get("relative_humidity_2m", 0),
            "precipitation": round(current.get("precipitation", 0), 2),
            "cloud_cover": current.get("cloud_cover", 0),
            "wind_speed": round(current.get("wind_speed_10m", 0), 1),
            "pressure": round(current.get("pressure_msl", 0), 1),
            "weather_code": today_weather_code,
            "weather_text": self._weather_code_to_text(today_weather_code, lang) if today_weather_code is not None else "—",
            "sunrise": sunrise.split("T")[1] if sunrise and "T" in sunrise else sunrise,
            "sunset": sunset.split("T")[1] if sunset and "T" in sunset else sunset,
            "uv_index": round(uv_index, 1) if uv_index is not None else None,
            "feels_like": round(current.get("temperature_2m", 0) - 1, 1),  # simplified
            "timestamp": datetime.now().isoformat(),
        }


# Singleton
weather_forecast_service = WeatherForecastService()
