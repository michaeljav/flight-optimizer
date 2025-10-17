# flights/cli.py
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django
django.setup()

from datetime import datetime, timedelta, timezone
from .utils import resolve_city_main_airport, cheapest_oneway, haversine_km

def run(from_city: str, to_cities: list[str]):
    dep = resolve_city_main_airport(from_city)
    best = None

    now = datetime.now(timezone.utc)
    date_from = now.strftime("%d/%m/%Y")
    date_to = (now + timedelta(days=1)).strftime("%d/%m/%Y")

    for city in to_cities:
        arr = resolve_city_main_airport(city)
        flight = cheapest_oneway(dep["airport_code"], arr["airport_code"], date_from, date_to, "USD")
        if not flight:
            continue

        price = float(flight["price"])
        dist_km = float(flight.get("distance") or haversine_km(dep["lat"], dep["lon"], arr["lat"], arr["lon"]))
        if dist_km <= 0:
            continue

        price_per_km = price / dist_km
        cand = {
            "destination": arr["city_name"],
            "airport": arr["airport_code"],
            "price": price,
            "distance_km": round(dist_km, 2),
            "price_per_km": round(price_per_km, 4),
        }
        if best is None or cand["price_per_km"] < best["price_per_km"]:
            best = cand

    return best

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Find cheapest flight per kilometer")
    parser.add_argument("--from", dest="from_city", required=True)
    parser.add_argument("--to", dest="to_cities", nargs="+", required=True)
    args = parser.parse_args()
    res = run(args.from_city, args.to_cities)
    if not res:
        print("No se encontraron vuelos en las próximas 24h.")
    else:
        print(res["destination"])
        print(f"${res['price_per_km']}/km")
