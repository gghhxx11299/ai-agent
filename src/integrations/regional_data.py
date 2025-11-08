"""Regional data integration for weather, agriculture, and satellite data"""

import requests
from datetime import datetime
from config.config import Config


class RegionalDataIntegration:
    """Integration for regional weather, agricultural, and satellite data"""

    def __init__(self):
        self.open_meteo_url = Config.OPEN_METEO_URL
        self.geocoding_url = Config.GEOCODING_URL
        self.agriculture_api_key = Config.AGRICULTURE_API_KEY
        self.agriculture_api_url = Config.AGRICULTURE_API_URL

    def _geocode_location(self, location: str) -> dict:
        """
        Geocode a location name to coordinates using Open-Meteo

        Args:
            location: City name or location

        Returns:
            Dictionary with coordinates and location info
        """
        try:
            response = requests.get(
                self.geocoding_url,
                params={
                    'name': location,
                    'count': 1,
                    'language': 'en',
                    'format': 'json'
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            if not data.get('results'):
                raise ValueError(f'Location "{location}" not found')

            result = data['results'][0]
            return {
                'latitude': result['latitude'],
                'longitude': result['longitude'],
                'name': result['name'],
                'country': result.get('country', ''),
                'admin1': result.get('admin1', '')
            }
        except Exception as e:
            raise ValueError(f'Geocoding failed: {e}')

    def _get_weather_description(self, code: int) -> str:
        """
        Get weather description from WMO code

        Args:
            code: WMO weather code

        Returns:
            Human-readable description
        """
        descriptions = {
            0: 'clear sky',
            1: 'mainly clear',
            2: 'partly cloudy',
            3: 'overcast',
            45: 'foggy',
            48: 'depositing rime fog',
            51: 'light drizzle',
            53: 'moderate drizzle',
            55: 'dense drizzle',
            61: 'slight rain',
            63: 'moderate rain',
            65: 'heavy rain',
            71: 'slight snow',
            73: 'moderate snow',
            75: 'heavy snow',
            77: 'snow grains',
            80: 'slight rain showers',
            81: 'moderate rain showers',
            82: 'violent rain showers',
            85: 'slight snow showers',
            86: 'heavy snow showers',
            95: 'thunderstorm',
            96: 'thunderstorm with slight hail',
            99: 'thunderstorm with heavy hail',
        }
        return descriptions.get(code, 'unknown')

    async def get_weather_data(self, location: str) -> dict:
        """
        Fetch weather data for a location using Open-Meteo

        Args:
            location: City name or coordinates

        Returns:
            Dictionary with weather data
        """
        try:
            # Step 1: Geocode the location
            coords = self._geocode_location(location)

            # Step 2: Fetch weather data from Open-Meteo
            response = requests.get(
                self.open_meteo_url,
                params={
                    'latitude': coords['latitude'],
                    'longitude': coords['longitude'],
                    'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,pressure_msl',
                    'hourly': 'temperature_2m,relative_humidity_2m,precipitation_probability,weather_code',
                    'timezone': 'auto',
                    'forecast_days': 3
                },
                timeout=15
            )
            response.raise_for_status()
            data = response.json()

            current = data['current']
            hourly = data['hourly']

            # Get next 8 hours of forecast
            forecast_data = []
            for i in range(min(8, len(hourly['time']))):
                forecast_data.append({
                    'datetime': hourly['time'][i],
                    'temp': hourly['temperature_2m'][i],
                    'description': self._get_weather_description(hourly['weather_code'][i]),
                    'humidity': hourly['relative_humidity_2m'][i],
                    'precipitation': hourly.get('precipitation_probability', [0])[i] if i < len(hourly.get('precipitation_probability', [])) else 0
                })

            return {
                'success': True,
                'location': f"{coords['name']}, {coords['country']}",
                'coordinates': {
                    'latitude': coords['latitude'],
                    'longitude': coords['longitude']
                },
                'current': {
                    'temperature': current['temperature_2m'],
                    'feelsLike': current['apparent_temperature'],
                    'humidity': current['relative_humidity_2m'],
                    'pressure': current['pressure_msl'],
                    'description': self._get_weather_description(current['weather_code']),
                    'windSpeed': current['wind_speed_10m'],
                    'precipitation': current.get('precipitation', 0)
                },
                'forecast': forecast_data,
                'source': 'Open-Meteo',
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Weather API error: {e}")
            return {
                'success': False,
                'error': str(e),
                'location': location,
                'message': f'Unable to fetch weather data for "{location}". {e}'
            }

    async def get_agricultural_data(self, location: str, crop_type: str = None) -> dict:
        """
        Fetch agricultural data for a region

        Args:
            location: Region name
            crop_type: Type of crop (optional)

        Returns:
            Dictionary with agricultural data
        """
        if not self.agriculture_api_key or not self.agriculture_api_url:
            print("⚠️  Agriculture API not configured. Using mock data.")
            return self._mock_agricultural_data(location, crop_type)

        try:
            response = requests.get(
                f"{self.agriculture_api_url}/crop-data",
                params={
                    'location': location,
                    'crop': crop_type,
                    'api_key': self.agriculture_api_key
                },
                timeout=10
            )
            response.raise_for_status()

            return {
                'success': True,
                'location': location,
                'data': response.json(),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Agriculture API error: {e}")
            return self._mock_agricultural_data(location, crop_type)

    async def get_soil_data(self, location: str) -> dict:
        """
        Fetch soil data for a location

        Args:
            location: Location name

        Returns:
            Dictionary with soil data
        """
        # Mock implementation - integrate with real soil data API
        return {
            'success': True,
            'location': location,
            'data': {
                'soilType': 'Loamy',
                'pH': 6.5,
                'nitrogen': 'Medium',
                'phosphorus': 'High',
                'potassium': 'Medium',
                'organicMatter': '3.2%',
                'recommendations': [
                    'Good drainage capacity',
                    'Suitable for most crops',
                    'Consider adding organic compost'
                ]
            },
            'mock': True,
            'timestamp': datetime.now().isoformat()
        }

    def _mock_agricultural_data(self, location: str, crop_type: str = None) -> dict:
        """Mock agricultural data for testing"""
        return {
            'success': True,
            'location': location,
            'cropType': crop_type or 'general',
            'data': {
                'soilMoisture': 68,
                'growingSeason': 'Active',
                'recommendedCrops': ['Maize', 'Wheat', 'Sorghum'],
                'alerts': [
                    'Optimal planting conditions',
                    'Monitor for pest activity'
                ],
                'yieldForecast': 'Above average expected'
            },
            'mock': True,
            'message': 'Mock data - configure Agriculture API for real data',
            'timestamp': datetime.now().isoformat()
        }
