from flights.utils import haversine_km
def test_haversine_positive():
    assert haversine_km(51.5, 0, 48.85, 2.35) > 300
