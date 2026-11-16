"""
Bangladesh 64 districts with GPS coordinates (lat/long)
Used for NASA POWER API weather lookup
Source: Bangladesh Bureau of Statistics
"""

DISTRICTS = [
    # Division: Barishal
    {"name": "Barishal", "bn_name": "বরিশাল", "lat": 22.7049, "lon": 90.3709, "division": "Barishal"},
    {"name": "Barguna", "bn_name": "বরগুনা", "lat": 22.1811, "lon": 90.1256, "division": "Barishal"},
    {"name": "Bhola", "bn_name": "ভোলা", "lat": 22.6858, "lon": 90.6483, "division": "Barishal"},
    {"name": "Jhalokati", "bn_name": "ঝালকাঠি", "lat": 22.6406, "lon": 90.1987, "division": "Barishal"},
    {"name": "Patuakhali", "bn_name": "পটুয়াখালী", "lat": 22.3593, "lon": 90.3318, "division": "Barishal"},
    {"name": "Pirojpur", "bn_name": "পিরোজপুর", "lat": 22.5840, "lon": 89.9678, "division": "Barishal"},

    # Division: Chattogram
    {"name": "Chattogram", "bn_name": "চট্টগ্রাম", "lat": 22.3569, "lon": 91.7832, "division": "Chattogram"},
    {"name": "Comilla", "bn_name": "কুমিল্লা", "lat": 23.4606, "lon": 91.1809, "division": "Chattogram"},
    {"name": "Cox's Bazar", "bn_name": "কক্সবাজার", "lat": 21.4272, "lon": 92.0058, "division": "Chattogram"},
    {"name": "Feni", "bn_name": "ফেনী", "lat": 23.0159, "lon": 91.3977, "division": "Chattogram"},
    {"name": "Brahmanbaria", "bn_name": "ব্রাহ্মণবাড়িয়া", "lat": 23.9570, "lon": 91.1110, "division": "Chattogram"},
    {"name": "Chandpur", "bn_name": "চাঁদপুর", "lat": 23.2376, "lon": 90.6505, "division": "Chattogram"},
    {"name": "Lakshmipur", "bn_name": "লক্ষ্মীপুর", "lat": 22.9425, "lon": 90.8414, "division": "Chattogram"},
    {"name": "Noakhali", "bn_name": "নোয়াখালী", "lat": 22.8700, "lon": 91.1000, "division": "Chattogram"},
    {"name": "Rangamati", "bn_name": "রাঙ্গামাটি", "lat": 22.6500, "lon": 92.1700, "division": "Chattogram"},
    {"name": "Khagrachhari", "bn_name": "খাগড়াছড়ি", "lat": 23.1200, "lon": 91.9800, "division": "Chattogram"},
    {"name": "Bandarban", "bn_name": "বান্দরবান", "lat": 22.1900, "lon": 92.2200, "division": "Chattogram"},

    # Division: Dhaka
    {"name": "Dhaka", "bn_name": "ঢাকা", "lat": 23.8103, "lon": 90.4125, "division": "Dhaka"},
    {"name": "Faridpur", "bn_name": "ফরিদপুর", "lat": 23.6010, "lon": 89.8333, "division": "Dhaka"},
    {"name": "Gazipur", "bn_name": "গাজীপুর", "lat": 24.0023, "lon": 90.4263, "division": "Dhaka"},
    {"name": "Gopalganj", "bn_name": "গোপালগঞ্জ", "lat": 23.0051, "lon": 89.8267, "division": "Dhaka"},
    {"name": "Kishoreganj", "bn_name": "কিশোরগঞ্জ", "lat": 24.4400, "lon": 90.7700, "division": "Dhaka"},
    {"name": "Madaripur", "bn_name": "মাদারীপুর", "lat": 23.1642, "lon": 90.1964, "division": "Dhaka"},
    {"name": "Manikganj", "bn_name": "মানিকগঞ্জ", "lat": 23.8644, "lon": 90.1315, "division": "Dhaka"},
    {"name": "Munshiganj", "bn_name": "মুন্সিগঞ্জ", "lat": 23.5288, "lon": 90.5300, "division": "Dhaka"},
    {"name": "Narayanganj", "bn_name": "নারায়ণগঞ্জ", "lat": 23.6238, "lon": 90.4963, "division": "Dhaka"},
    {"name": "Narsingdi", "bn_name": "নরসিংদী", "lat": 23.9232, "lon": 90.7191, "division": "Dhaka"},
    {"name": "Rajbari", "bn_name": "রাজবাড়ী", "lat": 23.7560, "lon": 89.6489, "division": "Dhaka"},
    {"name": "Shariatpur", "bn_name": "শরীয়তপুর", "lat": 23.2500, "lon": 90.4300, "division": "Dhaka"},
    {"name": "Tangail", "bn_name": "টাঙ্গাইল", "lat": 24.2513, "lon": 89.9167, "division": "Dhaka"},

    # Division: Khulna
    {"name": "Khulna", "bn_name": "খুলনা", "lat": 22.8456, "lon": 89.5403, "division": "Khulna"},
    {"name": "Bagerhat", "bn_name": "বাগেরহাট", "lat": 22.6517, "lon": 89.7862, "division": "Khulna"},
    {"name": "Chuadanga", "bn_name": "চুয়াডাঙ্গা", "lat": 23.6400, "lon": 88.8400, "division": "Khulna"},
    {"name": "Jessore", "bn_name": "যশোর", "lat": 23.1642, "lon": 89.2136, "division": "Khulna"},
    {"name": "Jhenaidah", "bn_name": "ঝিনাইদহ", "lat": 23.5448, "lon": 89.1639, "division": "Khulna"},
    {"name": "Magura", "bn_name": "মাগুরা", "lat": 23.4875, "lon": 89.4200, "division": "Khulna"},
    {"name": "Narail", "bn_name": "নড়াইল", "lat": 23.0260, "lon": 89.5128, "division": "Khulna"},
    {"name": "Satkhira", "bn_name": "সাতক্ষীরা", "lat": 22.7183, "lon": 89.0700, "division": "Khulna"},
    {"name": "Kushtia", "bn_name": "কুষ্টিয়া", "lat": 23.9013, "lon": 89.1204, "division": "Khulna"},
    {"name": "Meherpur", "bn_name": "মেহেরপুর", "lat": 23.7621, "lon": 88.6308, "division": "Khulna"},

    # Division: Mymensingh
    {"name": "Mymensingh", "bn_name": "ময়মনসিংহ", "lat": 24.7471, "lon": 90.4203, "division": "Mymensingh"},
    {"name": "Jamalpur", "bn_name": "জামালপুর", "lat": 24.9370, "lon": 89.9377, "division": "Mymensingh"},
    {"name": "Netrokona", "bn_name": "নেত্রকোণা", "lat": 24.8700, "lon": 90.7300, "division": "Mymensingh"},
    {"name": "Sherpur", "bn_name": "শেরপুর", "lat": 25.0170, "lon": 90.0183, "division": "Mymensingh"},

    # Division: Rajshahi
    {"name": "Rajshahi", "bn_name": "রাজশাহী", "lat": 24.3636, "lon": 88.6241, "division": "Rajshahi"},
    {"name": "Bogura", "bn_name": "বগুড়া", "lat": 24.8467, "lon": 89.3711, "division": "Rajshahi"},
    {"name": "Joypurhat", "bn_name": "জয়পুরহাট", "lat": 25.0967, "lon": 89.0222, "division": "Rajshahi"},
    {"name": "Naogaon", "bn_name": "নওগাঁ", "lat": 24.7936, "lon": 88.9317, "division": "Rajshahi"},
    {"name": "Natore", "bn_name": "নাটোর", "lat": 24.4206, "lon": 89.0000, "division": "Rajshahi"},
    {"name": "Nawabganj", "bn_name": "নবাবগঞ্জ", "lat": 24.5967, "lon": 88.2667, "division": "Rajshahi"},
    {"name": "Pabna", "bn_name": "পাবনা", "lat": 24.0042, "lon": 89.2399, "division": "Rajshahi"},
    {"name": "Sirajganj", "bn_name": "সিরাজগঞ্জ", "lat": 24.4700, "lon": 89.7100, "division": "Rajshahi"},

    # Division: Rangpur
    {"name": "Rangpur", "bn_name": "রংপুর", "lat": 25.7439, "lon": 89.2752, "division": "Rangpur"},
    {"name": "Dinajpur", "bn_name": "দিনাজপুর", "lat": 25.6217, "lon": 88.6344, "division": "Rangpur"},
    {"name": "Gaibandha", "bn_name": "গাইবান্ধা", "lat": 25.3288, "lon": 89.5411, "division": "Rangpur"},
    {"name": "Kurigram", "bn_name": "কুড়িগ্রাম", "lat": 25.8054, "lon": 89.6489, "division": "Rangpur"},
    {"name": "Lalmonirhat", "bn_name": "লালমনিরহাট", "lat": 25.9917, "lon": 89.2847, "division": "Rangpur"},
    {"name": "Nilphamari", "bn_name": "নীলফামারী", "lat": 25.9308, "lon": 88.8560, "division": "Rangpur"},
    {"name": "Panchagarh", "bn_name": "পঞ্চগড়", "lat": 26.3400, "lon": 88.5500, "division": "Rangpur"},
    {"name": "Thakurgaon", "bn_name": "ঠাকুরগাঁ", "lat": 26.0333, "lon": 88.4667, "division": "Rangpur"},

    # Division: Sylhet
    {"name": "Sylhet", "bn_name": "সিলেট", "lat": 24.8949, "lon": 91.8687, "division": "Sylhet"},
    {"name": "Habiganj", "bn_name": "হবিগঞ্জ", "lat": 24.3749, "lon": 91.4155, "division": "Sylhet"},
    {"name": "Moulvibazar", "bn_name": "মৌলভীবাজার", "lat": 24.4829, "lon": 91.7778, "division": "Sylhet"},
    {"name": "Sunamganj", "bn_name": "সুনামগঞ্জ", "lat": 25.0658, "lon": 91.4167, "division": "Sylhet"},
]


def get_district_by_name(name):
    """Get district info by English name"""
    for d in DISTRICTS:
        if d["name"].lower() == name.lower():
            return d
    return None


def get_districts_by_division(division):
    """Get all districts in a division"""
    return [d for d in DISTRICTS if d["division"] == division]


def get_all_divisions():
    """Get all unique divisions"""
    return sorted(set(d["division"] for d in DISTRICTS))
