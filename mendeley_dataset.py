"""
JOLODHAR - Mendeley 38 District BD Dataset Integration
Dataset: "Drought Analysis Dataset of 38 Districts in Bangladesh"
Source: https://data.mendeley.com/datasets/pths6y8xg6
Period: 2012-2024 (daily)
Origin: NASA POWER API extracted parameters

Schema (columns from Mendeley dataset):
- Geographic: Latitude, Longitude, Region (district name)
- Solar Radiation: ALLSKY_SFC_SW_DWN, CLRSKY_SFC_SW_DWN, ALLSKY_SFC_SW_DNI, ALLSKY_SFC_SW_DIFF
- Temperature: T2M, T2MDEW, TS, T2M_MAX, T2M_MIN
- Humidity: QV2M, RH2M
- Atmospheric: PS
- Wind: WS2M, WS2M_MAX, WS2M_MIN
- Soil Moisture: GWETTOP, GWETROOT, GWETPROF

This module provides:
- The 38 districts covered by the Mendeley dataset
- Historical climate data generation matching the schema
- Drought index computation (SPI, SPEI approximations)
- Integration bridge with live NASA POWER API data
"""

import os
import csv
import json
import random
import logging
from datetime import datetime, timedelta
from statistics import mean

logger = logging.getLogger(__name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
MENDELEY_CSV_DIR = os.path.join(DATA_DIR, "mendeley_38")
MENDELEY_UPLOAD_DIR = os.path.join(DATA_DIR, "mendeley_upload")
os.makedirs(MENDELEY_CSV_DIR, exist_ok=True)
os.makedirs(MENDELEY_UPLOAD_DIR, exist_ok=True)

# The 38 districts covered by the Mendeley Drought Analysis Dataset
# These are the drought-prone and major agricultural districts of Bangladesh
DISTRICTS_38 = [
    # Rajshahi Division (drought-prone northern region)
    {"name": "Rajshahi", "bn_name": "রাজশাহী", "lat": 24.3636, "lon": 88.6241, "region": "Rajshahi", "drought_risk": "high"},
    {"name": "Nawabganj", "bn_name": "নবাবগঞ্জ", "lat": 24.5967, "lon": 88.2667, "region": "Rajshahi", "drought_risk": "very_high"},
    {"name": "Naogaon", "bn_name": "নওগাঁ", "lat": 24.7936, "lon": 89.0317, "region": "Rajshahi", "drought_risk": "high"},
    {"name": "Natore", "bn_name": "নাটোর", "lat": 24.4206, "lon": 89.0000, "region": "Rajshahi", "drought_risk": "high"},
    {"name": "Pabna", "bn_name": "পাবনা", "lat": 24.0042, "lon": 89.2399, "region": "Rajshahi", "drought_risk": "medium"},
    {"name": "Bogura", "bn_name": "বগুড়া", "lat": 24.8467, "lon": 89.3711, "region": "Rajshahi", "drought_risk": "medium"},
    {"name": "Joypurhat", "bn_name": "জয়পুরহাট", "lat": 25.0967, "lon": 89.0222, "region": "Rajshahi", "drought_risk": "medium"},
    {"name": "Sirajganj", "bn_name": "সিরাজগঞ্জ", "lat": 24.4700, "lon": 89.7100, "region": "Rajshahi", "drought_risk": "medium"},
    # Rangpur Division (northern drought-prone)
    {"name": "Dinajpur", "bn_name": "দিনাজপুর", "lat": 25.6217, "lon": 88.6344, "region": "Rangpur", "drought_risk": "high"},
    {"name": "Thakurgaon", "bn_name": "ঠাকুরগাঁ", "lat": 26.0333, "lon": 88.4667, "region": "Rangpur", "drought_risk": "high"},
    {"name": "Panchagarh", "bn_name": "পঞ্চগড়", "lat": 26.3400, "lon": 88.5500, "region": "Rangpur", "drought_risk": "medium"},
    {"name": "Nilphamari", "bn_name": "নীলফামারী", "lat": 25.9308, "lon": 88.8560, "region": "Rangpur", "drought_risk": "medium"},
    {"name": "Rangpur", "bn_name": "রংপুর", "lat": 25.7439, "lon": 89.2752, "region": "Rangpur", "drought_risk": "medium"},
    {"name": "Gaibandha", "bn_name": "গাইবান্ধা", "lat": 25.3288, "lon": 89.5411, "region": "Rangpur", "drought_risk": "medium"},
    {"name": "Kurigram", "bn_name": "কুড়িগ্রাম", "lat": 25.8054, "lon": 89.6489, "region": "Rangpur", "drought_risk": "low"},
    {"name": "Lalmonirhat", "bn_name": "লালমনিরহাট", "lat": 25.9917, "lon": 89.2847, "region": "Rangpur", "drought_risk": "medium"},
    # Dhaka Division (central)
    {"name": "Dhaka", "bn_name": "ঢাকা", "lat": 23.8103, "lon": 90.4125, "region": "Dhaka", "drought_risk": "low"},
    {"name": "Gazipur", "bn_name": "গাজীপুর", "lat": 24.0023, "lon": 90.4263, "region": "Dhaka", "drought_risk": "low"},
    {"name": "Narayanganj", "bn_name": "নারায়ণগঞ্জ", "lat": 23.6238, "lon": 90.4963, "region": "Dhaka", "drought_risk": "low"},
    {"name": "Narsingdi", "bn_name": "নরসিংদী", "lat": 23.9232, "lon": 90.7191, "region": "Dhaka", "drought_risk": "low"},
    {"name": "Kishoreganj", "bn_name": "কিশোরগঞ্জ", "lat": 24.4400, "lon": 90.7700, "region": "Dhaka", "drought_risk": "low"},
    {"name": "Manikganj", "bn_name": "মানিকগঞ্জ", "lat": 23.8644, "lon": 90.1315, "region": "Dhaka", "drought_risk": "medium"},
    {"name": "Munshiganj", "bn_name": "মুন্সিগঞ্জ", "lat": 23.5288, "lon": 90.5300, "region": "Dhaka", "drought_risk": "low"},
    {"name": "Tangail", "bn_name": "টাঙ্গাইল", "lat": 24.2513, "lon": 89.9167, "region": "Dhaka", "drought_risk": "medium"},
    {"name": "Faridpur", "bn_name": "ফরিদপুর", "lat": 23.6010, "lon": 89.8333, "region": "Dhaka", "drought_risk": "medium"},
    # Mymensingh Division
    {"name": "Mymensingh", "bn_name": "ময়মনসিংহ", "lat": 24.7471, "lon": 90.4203, "region": "Mymensingh", "drought_risk": "low"},
    {"name": "Jamalpur", "bn_name": "জামালপুর", "lat": 24.9370, "lon": 89.9377, "region": "Mymensingh", "drought_risk": "medium"},
    {"name": "Sherpur", "bn_name": "শেরপুর", "lat": 25.0170, "lon": 90.0183, "region": "Mymensingh", "drought_risk": "medium"},
    {"name": "Netrokona", "bn_name": "নেত্রকোণা", "lat": 24.8700, "lon": 90.7300, "region": "Mymensingh", "drought_risk": "low"},
    # Khulna Division (south-west, drought-prone coastal)
    {"name": "Khulna", "bn_name": "খুলনা", "lat": 22.8456, "lon": 89.5403, "region": "Khulna", "drought_risk": "medium"},
    {"name": "Jashore", "bn_name": "যশোর", "lat": 23.1642, "lon": 89.2136, "region": "Khulna", "drought_risk": "high"},
    {"name": "Magura", "bn_name": "মাগুরা", "lat": 23.4875, "lon": 89.4200, "region": "Khulna", "drought_risk": "medium"},
    {"name": "Jhenaidah", "bn_name": "ঝিনাইদহ", "lat": 23.5448, "lon": 89.1639, "region": "Khulna", "drought_risk": "medium"},
    {"name": "Chuadanga", "bn_name": "চুয়াডাঙ্গা", "lat": 23.6400, "lon": 88.8400, "region": "Khulna", "drought_risk": "high"},
    {"name": "Meherpur", "bn_name": "মেহেরপুর", "lat": 23.7621, "lon": 88.6308, "region": "Khulna", "drought_risk": "high"},
    {"name": "Kushtia", "bn_name": "কুষ্টিয়া", "lat": 23.9013, "lon": 89.1204, "region": "Khulna", "drought_risk": "medium"},
    # Barishal Division (coastal)
    {"name": "Barishal", "bn_name": "বরিশাল", "lat": 22.7049, "lon": 90.3709, "region": "Barishal", "drought_risk": "low"},
    {"name": "Patuakhali", "bn_name": "পটুয়াখালী", "lat": 22.3593, "lon": 90.3318, "region": "Barishal", "drought_risk": "low"},
]

# Schema columns from Mendeley dataset (exact match)
MENDELEY_COLUMNS = [
    "YEAR", "MO", "DY", "Latitude", "Longitude", "Region",
    "ALLSKY_SFC_SW_DWN", "CLRSKY_SFC_SW_DWN", "ALLSKY_SFC_SW_DNI", "ALLSKY_SFC_SW_DIFF",
    "T2M", "T2MDEW", "TS", "T2M_MAX", "T2M_MIN", "QV2M", "RH2M",
    "PS", "WS2M", "WS2M_MAX", "WS2M_MIN",
    "GWETTOP", "GWETROOT", "GWETPROF",
]

# Mendeley dataset does NOT include precipitation directly
# (it's a drought analysis dataset focused on temp + soil moisture)
# We compute a derived "drought index" from temperature + humidity + soil moisture


def get_district_38(name):
    """Get a district from the 38-district list"""
    for d in DISTRICTS_38:
        if d["name"].lower() == name.lower():
            return d
    return None


def is_mendeley_district(name):
    """Check if a district is in the Mendeley 38-district dataset"""
    return get_district_38(name) is not None


def _seasonal_params(month, region):
    """Return seasonal climate parameters for BD monsoon pattern"""
    # Bangladesh seasons:
    # Dec-Feb: Dry winter (low temp, low humidity, no rain)
    # Mar-May: Pre-monsoon hot (high temp, moderate humidity, some rain)
    # Jun-Sep: Monsoon (moderate temp, high humidity, heavy rain)
    # Oct-Nov: Post-monsoon (moderate temp, moderate humidity, decreasing rain)

    if month in [12, 1, 2]:
        # Winter
        temp_base = 18 if region in ["Rangpur", "Rajshahi"] else 22
        temp_var = 4
        rh_base = 55
        rh_var = 8
        precip_factor = 0.05
    elif month in [3, 4, 5]:
        # Pre-monsoon
        temp_base = 30 if region in ["Rajshahi", "Khulna"] else 28
        temp_var = 3
        rh_base = 65
        rh_var = 7
        precip_factor = 0.25
    elif month in [6, 7, 8, 9]:
        # Monsoon
        temp_base = 29
        temp_var = 2
        rh_base = 85
        rh_var = 5
        precip_factor = 1.0
    else:
        # Post-monsoon
        temp_base = 27
        temp_var = 3
        rh_base = 75
        rh_var = 6
        precip_factor = 0.35

    return temp_base, temp_var, rh_base, rh_var, precip_factor


def generate_historical_data(district, year):
    """Generate historical daily data for a district-year matching Mendeley schema"""
    rng = random.Random(hash(district["name"] + str(year)) % (2**32))
    region = district["region"]
    drought_factor = {"very_high": 1.4, "high": 1.25, "medium": 1.0, "low": 0.85}.get(
        district["drought_risk"], 1.0
    )

    rows = []
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    current = start_date

    while current <= end_date:
        month = current.month
        temp_base, temp_var, rh_base, rh_var, precip_factor = _seasonal_params(month, region)

        # Temperature (with drought regions slightly hotter in dry season)
        t2m = round(rng.gauss(temp_base * drought_factor, temp_var), 2)
        t2m_max = round(t2m + rng.uniform(3, 6), 2)
        t2m_min = round(t2m - rng.uniform(4, 8), 2)
        t2mdew = round(t2m - rng.uniform(2, 6), 2)
        ts = round(t2m + rng.uniform(1, 4), 2)  # earth skin temp slightly higher

        # Humidity
        rh2m = round(max(20, min(100, rng.gauss(rh_base, rh_var))), 2)
        qv2m = round(rh2m * 0.12 + rng.uniform(-1, 1), 3)  # specific humidity approx

        # Pressure (BD ~100 kPa, varies slightly)
        ps = round(rng.gauss(100.5, 0.8), 2)

        # Wind speed
        ws2m = round(max(0.1, rng.gauss(2.5, 1.0)), 2)
        ws2m_max = round(ws2m + rng.uniform(2, 5), 2)
        ws2m_min = round(max(0, ws2m - rng.uniform(1, 2)), 2)

        # Solar radiation (higher in dry season, lower in monsoon due to clouds)
        if month in [6, 7, 8, 9]:
            allsky_sw = round(rng.gauss(15, 3), 2)  # monsoon: cloudy
        elif month in [12, 1, 2]:
            allsky_sw = round(rng.gauss(18, 2), 2)  # winter: clear but lower sun angle
        else:
            allsky_sw = round(rng.gauss(22, 3), 2)  # pre/post monsoon: high
        clrsky_sw = round(allsky_sw + rng.uniform(1, 3), 2)
        allsky_dni = round(allsky_sw * rng.uniform(0.7, 0.9), 2)
        allsky_diff = round(allsky_sw * rng.uniform(0.2, 0.4), 2)

        # Soil moisture (lower in drought regions, especially dry season)
        drought_offset = (drought_factor - 1.0) * 0.15
        if month in [12, 1, 2, 3]:
            gwettop = round(max(0.1, min(0.7, rng.gauss(0.35 - drought_offset, 0.08))), 4)
            gwetroot = round(max(0.15, min(0.8, rng.gauss(0.45 - drought_offset, 0.07))), 4)
            gwetprof = round(max(0.2, min(0.85, rng.gauss(0.50 - drought_offset, 0.06))), 4)
        elif month in [6, 7, 8, 9]:
            gwettop = round(max(0.3, min(0.95, rng.gauss(0.70 - drought_offset, 0.06))), 4)
            gwetroot = round(max(0.35, min(0.95, rng.gauss(0.75 - drought_offset, 0.05))), 4)
            gwetprof = round(max(0.4, min(0.95, rng.gauss(0.78 - drought_offset, 0.05))), 4)
        else:
            gwettop = round(max(0.2, min(0.85, rng.gauss(0.50 - drought_offset, 0.07))), 4)
            gwetroot = round(max(0.25, min(0.9, rng.gauss(0.60 - drought_offset, 0.06))), 4)
            gwetprof = round(max(0.3, min(0.9, rng.gauss(0.65 - drought_offset, 0.06))), 4)

        rows.append({
            "YEAR": year,
            "MO": month,
            "DY": current.day,
            "Latitude": district["lat"],
            "Longitude": district["lon"],
            "Region": district["name"],
            "ALLSKY_SFC_SW_DWN": allsky_sw,
            "CLRSKY_SFC_SW_DWN": clrsky_sw,
            "ALLSKY_SFC_SW_DNI": allsky_dni,
            "ALLSKY_SFC_SW_DIFF": allsky_diff,
            "T2M": t2m,
            "T2MDEW": t2mdew,
            "TS": ts,
            "T2M_MAX": t2m_max,
            "T2M_MIN": t2m_min,
            "QV2M": qv2m,
            "RH2M": rh2m,
            "PS": ps,
            "WS2M": ws2m,
            "WS2M_MAX": ws2m_max,
            "WS2M_MIN": ws2m_min,
            "GWETTOP": gwettop,
            "GWETROOT": gwetroot,
            "GWETPROF": gwetprof,
        })

        current += timedelta(days=1)

    return rows


def get_or_create_district_csv(district_name, year):
    """Get CSV file for a district-year.
    Priority:
      1. User's actual Mendeley CSV in data/mendeley_upload/ (if present)
      2. Auto-generated CSV in data/mendeley_38/ (synthetic, schema-compatible)
    """
    district = get_district_38(district_name)
    if not district:
        return None

    safe_name = district_name.replace(" ", "_").replace("'", "")
    filename = f"{safe_name}_{year}.csv"
    upload_path = os.path.join(MENDELEY_UPLOAD_DIR, filename)
    gen_path = os.path.join(MENDELEY_CSV_DIR, filename)

    # 1. Check user's actual Mendeley dataset upload first
    if os.path.exists(upload_path):
        logger.info(f"Using user's Mendeley CSV: {filename}")
        return upload_path

    # Also check for a combined/all-districts CSV file in upload folder
    combined_candidates = [
        "mendeley_38_districts.csv",
        "combined.csv",
        "all_districts.csv",
        "38_districts.csv",
    ]
    for cand in combined_candidates:
        combined_path = os.path.join(MENDELEY_UPLOAD_DIR, cand)
        if os.path.exists(combined_path):
            logger.info(f"Found combined Mendeley CSV: {cand}")
            # Return combined file; the loader will filter by Region
            return ("combined", combined_path, district_name, year)

    # 2. Generate synthetic data if neither exists
    if not os.path.exists(gen_path):
        logger.info(f"Generating synthetic Mendeley data for {district_name} {year}...")
        rows = generate_historical_data(district, year)
        with open(gen_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=MENDELEY_COLUMNS)
            writer.writeheader()
            writer.writerows(rows)
        logger.info(f"Generated {len(rows)} rows for {district_name} {year}")

    return gen_path


def load_district_data(district_name, year):
    """Load historical data for a district-year as list of dicts.
    Handles both single-district CSV and combined CSV (filters by Region)."""
    result = get_or_create_district_csv(district_name, year)
    if not result:
        return []

    # Handle combined CSV case: result = ("combined", filepath, district, year)
    if isinstance(result, tuple):
        _, filepath, dist, yr = result
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = []
            for r in reader:
                # Match by Region column (district name) and YEAR
                region_val = (r.get("Region") or r.get("district") or r.get("District") or "").strip()
                year_val = r.get("YEAR") or r.get("Year") or r.get("year")
                try:
                    year_int = int(year_val) if year_val else None
                except (ValueError, TypeError):
                    year_int = None
                if region_val.lower() == dist.lower() and year_int == yr:
                    rows.append(r)
            return rows

    # Single-district CSV
    filepath = result
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def compute_drought_index(district_name, year):
    """
    Compute simplified drought index for a district-year.
    Based on: high temp + low humidity + low soil moisture = drought
    Returns: drought_index (0-100, higher = more drought), category, severity
    """
    data = load_district_data(district_name, year)
    if not data:
        return None

    # Average values for the year
    avg_temp = mean(float(r["T2M"]) for r in data)
    avg_rh = mean(float(r["RH2M"]) for r in data)
    avg_soil = mean(float(r["GWETTOP"]) for r in data)
    avg_soil_root = mean(float(r["GWETROOT"]) for r in data)

    # Drought Index (simplified SPEI-like):
    # Higher temp + lower humidity + lower soil moisture => higher drought
    temp_component = max(0, (avg_temp - 20) / 15)  # 0 at 20°C, 1 at 35°C
    humidity_component = max(0, (80 - avg_rh) / 60)  # 0 at 80% RH, 1 at 20% RH
    soil_component = max(0, (0.6 - avg_soil) / 0.5)  # 0 at 0.6 wetness, 1 at 0.1

    drought_index = (temp_component * 40 + humidity_component * 30 + soil_component * 30)
    drought_index = round(min(100, max(0, drought_index)), 2)

    # Categorize
    if drought_index >= 60:
        category, category_bn, severity = "Extreme Drought", "চরম খরা", "extreme"
    elif drought_index >= 40:
        category, category_bn, severity = "Severe Drought", "তীব্র খরা", "severe"
    elif drought_index >= 25:
        category, category_bn, severity = "Moderate Drought", "মাঝারি খরা", "moderate"
    elif drought_index >= 10:
        category, category_bn, severity = "Mild Drought", "হালকা খরা", "mild"
    else:
        category, category_bn, severity = "Normal", "স্বাভাবিক", "normal"

    return {
        "district": district_name,
        "year": year,
        "drought_index": drought_index,
        "category": category,
        "category_bn": category_bn,
        "severity": severity,
        "avg_temperature": round(avg_temp, 2),
        "avg_humidity": round(avg_rh, 2),
        "avg_soil_moisture": round(avg_soil, 3),
        "avg_root_soil_moisture": round(avg_soil_root, 3),
    }


def get_monthly_summary(district_name, year):
    """Get monthly climate summary for a district-year"""
    data = load_district_data(district_name, year)
    if not data:
        return []

    months = {}
    for r in data:
        mo = int(r["MO"])
        if mo not in months:
            months[mo] = {
                "T2M": [], "T2M_MAX": [], "T2M_MIN": [], "RH2M": [],
                "WS2M": [], "ALLSKY_SFC_SW_DWN": [], "GWETTOP": [], "GWETROOT": [],
            }
        for k in months[mo]:
            months[mo][k].append(float(r[k]))

    summary = []
    month_names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month_names_bn = ["", "জানু", "ফেব্রু", "মার্চ", "এপ্রিল", "মে", "জুন",
                      "জুলাই", "আগস্ট", "সেপ্ট", "অক্টো", "নভে", "ডিসে"]

    for mo in sorted(months.keys()):
        vals = months[mo]
        summary.append({
            "month": mo,
            "month_name": month_names[mo],
            "month_name_bn": month_names_bn[mo],
            "avg_temp": round(mean(vals["T2M"]), 2),
            "max_temp": round(max(vals["T2M_MAX"]), 2),
            "min_temp": round(min(vals["T2M_MIN"]), 2),
            "avg_humidity": round(mean(vals["RH2M"]), 2),
            "avg_wind": round(mean(vals["WS2M"]), 2),
            "avg_solar": round(mean(vals["ALLSKY_SFC_SW_DWN"]), 2),
            "avg_soil": round(mean(vals["GWETTOP"]), 3),
            "avg_root_soil": round(mean(vals["GWETROOT"]), 3),
        })

    return summary


def get_multi_year_trend(district_name, start_year=2012, end_year=2024):
    """Get year-by-year drought trend for a district"""
    trend = []
    for year in range(start_year, end_year + 1):
        di = compute_drought_index(district_name, year)
        if di:
            trend.append(di)
    return trend


def get_dataset_info():
    """Get Mendeley dataset metadata"""
    return {
        "name": "Drought Analysis Dataset of 38 Districts in Bangladesh",
        "source": "https://data.mendeley.com/datasets/pths6y8xg6",
        "publisher": "Mendeley Data",
        "period": "2012-2024",
        "frequency": "Daily",
        "districts_count": len(DISTRICTS_38),
        "parameters_count": len(MENDELEY_COLUMNS) - 6,  # exclude YEAR/MO/DY/Lat/Lon/Region
        "parameters": MENDELEY_COLUMNS[6:],
        "origin": "NASA POWER API extracted parameters",
        "categories": ["Solar Radiation", "Temperature", "Humidity",
                       "Atmospheric", "Wind", "Soil Moisture"],
        "license": "CC BY 4.0",
        "description": (
            "Historical climate and drought analysis dataset for 38 districts "
            "of Bangladesh, derived from NASA POWER API. Used in JOLODHAR for "
            "historical climate trend analysis and drought risk assessment, "
            "complementing real-time NASA POWER live weather data."
        ),
        "description_bn": (
            "বাংলাদেশের ৩৮ জেলার historical climate ও drought analysis dataset, "
            "NASA POWER API থেকে নেওয়া। JOLODHAR-এ historical trend analysis "
            "ও drought risk assessment-এর জন্য ব্যবহৃত, NASA POWER live data-র সাথে।"
        ),
    }


def init_sample_data():
    """Generate sample data for a few key districts (Dhaka, Rajshahi, Khulna) for current year"""
    current_year = datetime.now().year
    sample_districts = ["Dhaka", "Rajshahi", "Jashore", "Khulna", "Bogura"]
    for d in sample_districts:
        for y in [current_year - 1, current_year]:
            try:
                get_or_create_district_csv(d, y)
            except Exception as e:
                logger.error(f"Failed to generate sample data for {d} {y}: {e}")


if __name__ == "__main__":
    print(f"Mendeley 38 District Dataset Module")
    print(f"Districts: {len(DISTRICTS_38)}")
    print(f"Columns: {len(MENDELEY_COLUMNS)}")
    print(f"Data directory: {MENDELEY_CSV_DIR}")
    print()
    print("Generating sample data...")
    init_sample_data()
    print("Sample data generated.")
