from geopy import Nominatim


class GeolocatorService:
    """Handles geolocation queries using geopy."""

    def __init__(self):
        self.geolocator = Nominatim(user_agent="weather_app")

    def get_location(self, query):
        """Returns a location object from a search query."""
        try:
            return self.geolocator.geocode(query)
        except Exception as e:
            print(f"Geocoder error: {e}")
            return None
