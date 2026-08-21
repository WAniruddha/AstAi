from __future__ import annotations

from dataclasses import dataclass

INDIA_TIMEZONE = "Asia/Kolkata"


@dataclass(frozen=True, slots=True)
class IndiaPlace:
    name: str
    state: str
    latitude: float
    longitude: float
    timezone: str = INDIA_TIMEZONE

    @property
    def label(self) -> str:
        return f"{self.name}, {self.state}, India"


# v0.5.1 starter gazetteer. It intentionally covers all States/UTs plus major
# population centres while keeping the application fully offline. A future
# gazetteer release can replace/extend this catalog without changing the chart
# engine or BirthData contract.
INDIA_PLACES: tuple[IndiaPlace, ...] = (
    IndiaPlace("Visakhapatnam", "Andhra Pradesh", 17.6868, 83.2185),
    IndiaPlace("Vijayawada", "Andhra Pradesh", 16.5062, 80.6480),
    IndiaPlace("Guntur", "Andhra Pradesh", 16.3067, 80.4365),
    IndiaPlace("Tirupati", "Andhra Pradesh", 13.6288, 79.4192),
    IndiaPlace("Nellore", "Andhra Pradesh", 14.4426, 79.9865),
    IndiaPlace("Kurnool", "Andhra Pradesh", 15.8281, 78.0373),
    IndiaPlace("Itanagar", "Arunachal Pradesh", 27.0844, 93.6053),
    IndiaPlace("Guwahati", "Assam", 26.1445, 91.7362),
    IndiaPlace("Dibrugarh", "Assam", 27.4728, 94.9120),
    IndiaPlace("Silchar", "Assam", 24.8333, 92.7789),
    IndiaPlace("Jorhat", "Assam", 26.7509, 94.2037),
    IndiaPlace("Patna", "Bihar", 25.5941, 85.1376),
    IndiaPlace("Gaya", "Bihar", 24.7914, 85.0002),
    IndiaPlace("Muzaffarpur", "Bihar", 26.1209, 85.3647),
    IndiaPlace("Bhagalpur", "Bihar", 25.2425, 86.9842),
    IndiaPlace("Raipur", "Chhattisgarh", 21.2514, 81.6296),
    IndiaPlace("Bilaspur", "Chhattisgarh", 22.0797, 82.1409),
    IndiaPlace("Durg", "Chhattisgarh", 21.1904, 81.2849),
    IndiaPlace("Panaji", "Goa", 15.4909, 73.8278),
    IndiaPlace("Margao", "Goa", 15.2832, 73.9862),
    IndiaPlace("Vasco da Gama", "Goa", 15.3860, 73.8440),
    IndiaPlace("Ahmedabad", "Gujarat", 23.0225, 72.5714),
    IndiaPlace("Surat", "Gujarat", 21.1702, 72.8311),
    IndiaPlace("Vadodara", "Gujarat", 22.3072, 73.1812),
    IndiaPlace("Rajkot", "Gujarat", 22.3039, 70.8022),
    IndiaPlace("Gandhinagar", "Gujarat", 23.2156, 72.6369),
    IndiaPlace("Bhavnagar", "Gujarat", 21.7645, 72.1519),
    IndiaPlace("Gurugram", "Haryana", 28.4595, 77.0266),
    IndiaPlace("Faridabad", "Haryana", 28.4089, 77.3178),
    IndiaPlace("Panipat", "Haryana", 29.3909, 76.9635),
    IndiaPlace("Ambala", "Haryana", 30.3782, 76.7767),
    IndiaPlace("Hisar", "Haryana", 29.1492, 75.7217),
    IndiaPlace("Shimla", "Himachal Pradesh", 31.1048, 77.1734),
    IndiaPlace("Dharamshala", "Himachal Pradesh", 32.2190, 76.3234),
    IndiaPlace("Mandi", "Himachal Pradesh", 31.5892, 76.9182),
    IndiaPlace("Ranchi", "Jharkhand", 23.3441, 85.3096),
    IndiaPlace("Jamshedpur", "Jharkhand", 22.8046, 86.2029),
    IndiaPlace("Dhanbad", "Jharkhand", 23.7957, 86.4304),
    IndiaPlace("Bokaro", "Jharkhand", 23.6693, 86.1511),
    IndiaPlace("Bengaluru", "Karnataka", 12.9716, 77.5946),
    IndiaPlace("Mysuru", "Karnataka", 12.2958, 76.6394),
    IndiaPlace("Mangaluru", "Karnataka", 12.9141, 74.8560),
    IndiaPlace("Hubballi", "Karnataka", 15.3647, 75.1240),
    IndiaPlace("Belagavi", "Karnataka", 15.8497, 74.4977),
    IndiaPlace("Shivamogga", "Karnataka", 13.9299, 75.5681),
    IndiaPlace("Thiruvananthapuram", "Kerala", 8.5241, 76.9366),
    IndiaPlace("Kochi", "Kerala", 9.9312, 76.2673),
    IndiaPlace("Kozhikode", "Kerala", 11.2588, 75.7804),
    IndiaPlace("Thrissur", "Kerala", 10.5276, 76.2144),
    IndiaPlace("Kannur", "Kerala", 11.8745, 75.3704),
    IndiaPlace("Kollam", "Kerala", 8.8932, 76.6141),
    IndiaPlace("Bhopal", "Madhya Pradesh", 23.2599, 77.4126),
    IndiaPlace("Indore", "Madhya Pradesh", 22.7196, 75.8577),
    IndiaPlace("Jabalpur", "Madhya Pradesh", 23.1815, 79.9864),
    IndiaPlace("Gwalior", "Madhya Pradesh", 26.2183, 78.1828),
    IndiaPlace("Ujjain", "Madhya Pradesh", 23.1765, 75.7885),
    IndiaPlace("Mumbai", "Maharashtra", 19.0760, 72.8777),
    IndiaPlace("Pune", "Maharashtra", 18.5204, 73.8567),
    IndiaPlace("Nagpur", "Maharashtra", 21.1458, 79.0882),
    IndiaPlace("Nashik", "Maharashtra", 19.9975, 73.7898),
    IndiaPlace("Thane", "Maharashtra", 19.2183, 72.9781),
    IndiaPlace("Chhatrapati Sambhajinagar", "Maharashtra", 19.8762, 75.3433),
    IndiaPlace("Kolhapur", "Maharashtra", 16.7050, 74.2433),
    IndiaPlace("Solapur", "Maharashtra", 17.6599, 75.9064),
    IndiaPlace("Amravati", "Maharashtra", 20.9374, 77.7796),
    IndiaPlace("Nanded", "Maharashtra", 19.1383, 77.3210),
    IndiaPlace("Imphal", "Manipur", 24.8170, 93.9368),
    IndiaPlace("Shillong", "Meghalaya", 25.5788, 91.8933),
    IndiaPlace("Aizawl", "Mizoram", 23.7271, 92.7176),
    IndiaPlace("Kohima", "Nagaland", 25.6751, 94.1086),
    IndiaPlace("Dimapur", "Nagaland", 25.9091, 93.7266),
    IndiaPlace("Bhubaneswar", "Odisha", 20.2961, 85.8245),
    IndiaPlace("Cuttack", "Odisha", 20.4625, 85.8830),
    IndiaPlace("Rourkela", "Odisha", 22.2604, 84.8536),
    IndiaPlace("Puri", "Odisha", 19.8135, 85.8312),
    IndiaPlace("Sambalpur", "Odisha", 21.4669, 83.9812),
    IndiaPlace("Ludhiana", "Punjab", 30.9010, 75.8573),
    IndiaPlace("Amritsar", "Punjab", 31.6340, 74.8723),
    IndiaPlace("Jalandhar", "Punjab", 31.3260, 75.5762),
    IndiaPlace("Patiala", "Punjab", 30.3398, 76.3869),
    IndiaPlace("Bathinda", "Punjab", 30.2110, 74.9455),
    IndiaPlace("Jaipur", "Rajasthan", 26.9124, 75.7873),
    IndiaPlace("Jodhpur", "Rajasthan", 26.2389, 73.0243),
    IndiaPlace("Udaipur", "Rajasthan", 24.5854, 73.7125),
    IndiaPlace("Kota", "Rajasthan", 25.2138, 75.8648),
    IndiaPlace("Ajmer", "Rajasthan", 26.4499, 74.6399),
    IndiaPlace("Bikaner", "Rajasthan", 28.0229, 73.3119),
    IndiaPlace("Gangtok", "Sikkim", 27.3389, 88.6065),
    IndiaPlace("Chennai", "Tamil Nadu", 13.0827, 80.2707),
    IndiaPlace("Coimbatore", "Tamil Nadu", 11.0168, 76.9558),
    IndiaPlace("Madurai", "Tamil Nadu", 9.9252, 78.1198),
    IndiaPlace("Tiruchirappalli", "Tamil Nadu", 10.7905, 78.7047),
    IndiaPlace("Salem", "Tamil Nadu", 11.6643, 78.1460),
    IndiaPlace("Tirunelveli", "Tamil Nadu", 8.7139, 77.7567),
    IndiaPlace("Hyderabad", "Telangana", 17.3850, 78.4867),
    IndiaPlace("Warangal", "Telangana", 17.9689, 79.5941),
    IndiaPlace("Nizamabad", "Telangana", 18.6725, 78.0941),
    IndiaPlace("Karimnagar", "Telangana", 18.4386, 79.1288),
    IndiaPlace("Agartala", "Tripura", 23.8315, 91.2868),
    IndiaPlace("Lucknow", "Uttar Pradesh", 26.8467, 80.9462),
    IndiaPlace("Kanpur", "Uttar Pradesh", 26.4499, 80.3319),
    IndiaPlace("Varanasi", "Uttar Pradesh", 25.3176, 82.9739),
    IndiaPlace("Agra", "Uttar Pradesh", 27.1767, 78.0081),
    IndiaPlace("Prayagraj", "Uttar Pradesh", 25.4358, 81.8463),
    IndiaPlace("Noida", "Uttar Pradesh", 28.5355, 77.3910),
    IndiaPlace("Ghaziabad", "Uttar Pradesh", 28.6692, 77.4538),
    IndiaPlace("Meerut", "Uttar Pradesh", 28.9845, 77.7064),
    IndiaPlace("Gorakhpur", "Uttar Pradesh", 26.7606, 83.3732),
    IndiaPlace("Dehradun", "Uttarakhand", 30.3165, 78.0322),
    IndiaPlace("Haridwar", "Uttarakhand", 29.9457, 78.1642),
    IndiaPlace("Haldwani", "Uttarakhand", 29.2183, 79.5130),
    IndiaPlace("Kolkata", "West Bengal", 22.5726, 88.3639),
    IndiaPlace("Howrah", "West Bengal", 22.5958, 88.2636),
    IndiaPlace("Durgapur", "West Bengal", 23.5204, 87.3119),
    IndiaPlace("Siliguri", "West Bengal", 26.7271, 88.3953),
    IndiaPlace("Asansol", "West Bengal", 23.6739, 86.9524),
    IndiaPlace("Port Blair", "Andaman and Nicobar Islands", 11.6234, 92.7265),
    IndiaPlace("Chandigarh", "Chandigarh", 30.7333, 76.7794),
    IndiaPlace("Daman", "Dadra and Nagar Haveli and Daman and Diu", 20.3974, 72.8328),
    IndiaPlace("Silvassa", "Dadra and Nagar Haveli and Daman and Diu", 20.2739, 73.0083),
    IndiaPlace("New Delhi", "Delhi", 28.6139, 77.2090),
    IndiaPlace("Delhi", "Delhi", 28.7041, 77.1025),
    IndiaPlace("Srinagar", "Jammu and Kashmir", 34.0837, 74.7973),
    IndiaPlace("Jammu", "Jammu and Kashmir", 32.7266, 74.8570),
    IndiaPlace("Leh", "Ladakh", 34.1526, 77.5771),
    IndiaPlace("Kavaratti", "Lakshadweep", 10.5667, 72.6420),
    IndiaPlace("Puducherry", "Puducherry", 11.9416, 79.8083),
)


def india_states() -> tuple[str, ...]:
    return tuple(sorted({place.state for place in INDIA_PLACES}))


def places_for_state(state: str) -> tuple[IndiaPlace, ...]:
    return tuple(sorted((p for p in INDIA_PLACES if p.state == state), key=lambda p: p.name))


def find_india_place(state: str, name: str) -> IndiaPlace:
    normalized = name.strip().casefold()
    for place in INDIA_PLACES:
        if place.state == state and place.name.casefold() == normalized:
            return place
    raise KeyError(f"Unknown India place in starter gazetteer: {name}, {state}")
