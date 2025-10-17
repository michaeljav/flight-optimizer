import math
import os
import requests

# Try Django settings; fall back to .env if CLI or other context
try:
    from django.conf import settings
    TEQUILA_BASE_URL = getattr(settings, "TEQUILA_BASE_URL", None)
    TEQUILA_API_KEY = getattr(settings, "TEQUILA_API_KEY", None)
except Exception:
    TEQUILA_BASE_URL = None
    TEQUILA_API_KEY = None

if not TEQUILA_BASE_URL or not TEQUILA_API_KEY:
    # Fallback so the CLI can run even without Django fully booted
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.getcwd(), ".env"))
    TEQUILA_BASE_URL = os.getenv("TEQUILA_BASE_URL", "https://tequila-api.kiwi.com")
    TEQUILA_API_KEY = os.getenv("TEQUILA_API_KEY", "")


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return 2 * R * math.asin(math.sqrt(a))


def tequila_get(path, params):
    base = TEQUILA_BASE_URL.rstrip("/")
    url = f"{base}/{path.lstrip('/')}"
    headers = {
        "apikey": TEQUILA_API_KEY,
        "Content-Type": "application/json",
        "accept-encoding": "gzip",
    }
    r = requests.get(url, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def _pick_main_airport_by_radius(lat, lon, radius_km="200", limit=20):
    """Find the 'main' airport around a coordinate by Kiwi rank (lower rank = more prominent)."""
    airports = tequila_get(
        "locations/radius",
        {
            "lat": lat,
            "lon": lon,
            "radius": str(radius_km),
            "location_types": "airport",
            "limit": limit,
            "active_only": "true",
        },
    ).get("locations", [])
    if not airports:
        return None
    airports_sorted = sorted(airports, key=lambda a: int(a.get("rank", "0")))
    main = airports_sorted[0]
    return {
        "city_code": (main.get("city") or {}).get("code") or main.get("code"),
        "city_name": (main.get("city") or {}).get("name") or main.get("name"),
        "airport_code": main["code"],
        "airport_name": main["name"],
        "lat": float(main["location"]["lat"]),
        "lon": float(main["location"]["lon"]),
    }


def resolve_city_main_airport(term: str):
    """
    Resolve a user-provided place name to a 'main' airport.
    Tries: city -> airport -> country/territory.
    Includes a few synonyms for common country names in Spanish.
    """
    q = (term or "").strip()
    if not q:
        raise ValueError("Empty location term.")

    # Useful synonyms (Spanish -> main city) to reduce confusion
    synonyms = {
        "puerto rico": "San Juan",
        "republica dominicana": "Santo Domingo",
        "república dominicana": "Santo Domingo",
        "rd": "Santo Domingo",
        "usa": "New York",
        "estados unidos": "New York",
        "uk": "London",
        "inglaterra": "London",
    }
    q = synonyms.get(q.lower(), q)

    # 1) City
    data_city = tequila_get(
        "locations/query",
        {"term": q, "location_types": "city", "limit": 1, "active_only": "true"},
    )
    if data_city.get("locations"):
        city = data_city["locations"][0]
        lat = float(city["location"]["lat"])
        lon = float(city["location"]["lon"])
        main = _pick_main_airport_by_radius(lat, lon, radius_km="80")  # tight radius for city
        if main:
            main["city_name"] = city["name"]
            main["city_code"] = city.get("code") or city.get("id")
            return main

    # 2) Airport (exact)
    data_airport = tequila_get(
        "locations/query",
        {"term": q, "location_types": "airport", "limit": 1, "active_only": "true"},
    )
    if data_airport.get("locations"):
        ap = data_airport["locations"][0]
        return {
            "city_code": (ap.get("city") or {}).get("code") or ap.get("code"),
            "city_name": (ap.get("city") or {}).get("name") or ap.get("name"),
            "airport_code": ap["code"],
            "airport_name": ap["name"],
            "lat": float(ap["location"]["lat"]),
            "lon": float(ap["location"]["lon"]),
        }

    # 3) Country/Territory
    data_country = tequila_get(
        "locations/query",
        {"term": q, "location_types": "country", "limit": 1, "active_only": "true"},
    )
    if data_country.get("locations"):
        country = data_country["locations"][0]
        lat = float(country["location"]["lat"])
        lon = float(country["location"]["lon"])
        main = _pick_main_airport_by_radius(lat, lon, radius_km="300")
        if main:
            return main

    # Nothing matched
    raise ValueError(f"Location not found: {term}")


def cheapest_oneway(from_code, to_code, date_from, date_to, currency="USD"):
    res = tequila_get(
        "v2/search",
        {
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
            "limit": 1,
        },
    )
    flights = res.get("data", [])
    return flights[0] if flights else None
