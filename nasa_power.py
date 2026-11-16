"""
JOLODHAR - NASA POWER API Integration Service
Fetches weather data from NASA POWER API for Bangladesh districts
Provides current conditions + recent historical data
"""

import requests
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class NASAPowerService:
    """NASA POWER API client for JOLODHAR"""

    BASE_URL = "https://power.larc.nasa.gov/api/temporal"

    # Parameters we use
    # PRECTOTCORR = Precipitation (mm/day)
    # T2M = Temperature at 2m (°C)
    # T2M_MAX / T2M_MIN = max/min temp
    # RH2M = Relative humidity at 2m (%)
    # WS10M = Wind speed at 10m (m/s)
    # PS = Surface pressure (kPa)
    # ALLSKY_SFC_SW_DWN = All sky insolation (kW-hr/m^2/day)
    # CLRSKY_SFC_SW_DWN = Clear sky insolation
    # T2MDEW = Dew point
    # CLOUD_AMT = Cloud amount (%)

    def __init__(self, timeout=30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "JOLODHAR/1.0 (Team Aphelion - NASA Space Apps)"
        })

    def get_daily_weather(self, lat, lon, start_date, end_date):
        """
        Fetch daily weather from NASA POWER API
        Returns dict of parameter -> list of (date, value)
        """
        params_str = "PRECTOTCORR,T2M,T2M_MAX,T2M_MIN,RH2M,WS10M,PS,ALLSKY_SFC_SW_DWN,T2MDEW,CLOUD_AMT"
        url = f"{self.BASE_URL}/daily/point"
        params = {
            "parameters": params_str,
            "community": "AG",
            "longitude": round(float(lon), 4),
            "latitude": round(float(lat), 4),
            "start": start_date,
            "end": end_date,
            "format": "JSON",
        }

        try:
            resp = self.session.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            return self._parse_response(data, start_date, end_date)
        except requests.exceptions.RequestException as e:
            logger.error(f"NASA POWER API error: {e}")
            return None
        except Exception as e:
            logger.error(f"NASA POWER parse error: {e}")
            return None

    def _parse_response(self, data, start_date, end_date):
        """Parse NASA POWER API response into clean dict.
        NASA POWER returns records in two possible formats:
          - List of dicts: [{"date": "20240101", "value": 0.5}, ...]
          - Dict mapping:  {"20240101": 0.5, ...}
        Handle both robustly.
        """
        try:
            props = data["properties"]["parameter"]
            parsed = {}
            for param, records in props.items():
                param_data = {}
                if isinstance(records, list):
                    # list of dicts [{"date":..., "value":...}]
                    for r in records:
                        if isinstance(r, dict) and "date" in r and "value" in r:
                            param_data[r["date"]] = r["value"]
                elif isinstance(records, dict):
                    # dict mapping {date: value}
                    for k, v in records.items():
                        param_data[str(k)] = v
                parsed[param] = param_data
            parsed["_meta"] = {
                "start": start_date,
                "end": end_date,
                "lon": data.get("geometry", {}).get("coordinates", [None, None])[0],
                "lat": data.get("geometry", {}).get("coordinates", [None, None])[1],
            }
            return parsed
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"NASA POWER parse error: {e}")
            return None

    def get_recent_weather(self, lat, lon, days=7):
        """
        Get weather for the last N days (including today)
        Returns daily weather data
        """
        today = datetime.now()
        start = today - timedelta(days=days)
        return self.get_daily_weather(
            lat, lon,
            start.strftime("%Y%m%d"),
            today.strftime("%Y%m%d"),
        )

    def get_current_summary(self, lat, lon):
        """
        Get a summary of current conditions using today + yesterday data
        Returns a clean dict with current weather info
        """
        data = self.get_recent_weather(lat, lon, days=2)
        if not data:
            return None

        today_str = datetime.now().strftime("%Y%m%d")
        yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")

        def get_val(param, date):
            try:
                return data.get(param, {}).get(date, None)
            except Exception:
                return None

        summary = {
            "temperature": get_val("T2M", today_str),
            "temperature_max": get_val("T2M_MAX", today_str),
            "temperature_min": get_val("T2M_MIN", today_str),
            "humidity": get_val("RH2M", today_str),
            "precipitation": get_val("PRECTOTCORR", today_str),
            "wind_speed": get_val("WS10M", today_str),
            "pressure": get_val("PS", today_str),
            "cloud_cover": get_val("CLOUD_AMT", today_str),
            "dew_point": get_val("T2MDEW", today_str),
            "solar_radiation": get_val("ALLSKY_SFC_SW_DWN", today_str),
            "yesterday_precipitation": get_val("PRECTOTCORR", yesterday_str),
            "yesterday_humidity": get_val("RH2M", yesterday_str),
            "yesterday_cloud": get_val("CLOUD_AMT", yesterday_str),
            "data_source": "NASA POWER API",
            "timestamp": datetime.now().isoformat(),
        }
        # Round floats
        for k, v in summary.items():
            if isinstance(v, float):
                summary[k] = round(v, 2)
        return summary

    def get_weekly_history(self, lat, lon, weeks=2):
        """Get last 2 weeks of daily data for trend analysis"""
        today = datetime.now()
        start = today - timedelta(days=weeks * 7)
        return self.get_daily_weather(
            lat, lon,
            start.strftime("%Y%m%d"),
            today.strftime("%Y%m%d"),
        )


# Singleton
nasa_power_service = NASAPowerService()
