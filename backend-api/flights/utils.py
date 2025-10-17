import math
import requests
from django.conf import settings

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def tequila_get(path, params):
    base = settings.TEQUILA_BASE_URL.rstrip("/")
    url = f"{base}/{path.lstrip('/')}"
    headers = {
        "apikey": settings.TEQUILA_API_KEY,
        "Content-Type": "application/json",
        "accept-encoding": "gzip",
    }
    r = requests.get(url, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def resolve_city_main_airport(city_name: str):
    # 1) resolver ciudad
    data = tequila_get("locations/query", {
        "term": city_name,
        "location_types": "city",
        "limit": 1,
        "active_only": "true"
    })
    if not data.get("locations"):
        raise ValueError(f"Ciudad no encontrada: {city_name}")

    city = data["locations"][0]
    lat = float(city["location"]["lat"])
    lon = float(city["location"]["lon"])

    # 2) buscar aeropuertos cercanos y elegir el de mejor "rank"
    airports = tequila_get("locations/radius", {
        "lat": lat, "lon": lon, "radius": "80",
        "location_types": "airport",
        "limit": 10, "active_only": "true"
    }).get("locations", [])

    if not airports:
        raise ValueError(f"Sin aeropuertos para: {city_name}")

    airports_sorted = sorted(airports, key=lambda a: int(a.get("rank", "0")))
    main = airports_sorted[0]

    return {
        "city_code": city.get("code") or city.get("id"),
        "city_name": city["name"],
        "airport_code": main["code"],
        "airport_name": main["name"],
        "lat": float(main["location"]["lat"]),
        "lon": float(main["location"]["lon"]),
    }

def cheapest_oneway(from_code, to_code, date_from, date_to, currency="USD"):
    res = tequila_get("v2/search", {
        "fly_from": from_code,
        "fly_to": to_code,
        "date_from": date_from,
        "date_to": date_to,
        "flight_type": "oneway",
        "one_for_city": 0,
        "one_per_date": 0,
        "adults": 1,
        "curr": currency,
        "sort": "price",
        "limit": 1
    })
    flights = res.get("data", [])
    return flights[0] if flights else None
