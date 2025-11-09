"""Regional data integration for weather, agriculture, and satellite data"""

import httpx
import json
from datetime import datetime
from config.config import Config


class RegionalDataIntegration:
    """Integration for regional weather, agricultural, and satellite data"""

    def __init__(self):
        self.open_meteo_url = Config.OPEN_METEO_URL
        self.geocoding_url = Config.GEOCODING_URL
        self.agriculture_api_key = Config.AGRICULTURE_API_KEY
        self.agriculture_api_url = Config.AGRICULTURE_API_URL
        self.client = httpx.AsyncClient(timeout=15.0)

    async def _geocode_location(self, location: str) -> dict:
        """
        Geocode a location name to coordinates using Open-Meteo

        Args:
            location: City name or location

        Returns:
            Dictionary with coordinates and location info
        """
        try:
            response = await self.client.get(
                self.geocoding_url,
                params={
                    'name': location,
                    'count': 1,
                    'language': 'en',
                    'format': 'json'
                }
            )
            response.raise_for_status()

            # Safe JSON parsing with EOF error handling
            try:
                data = response.json()
            except (ValueError, json.JSONDecodeError) as json_err:
                # Try to parse response text directly
                response_text = response.text if hasattr(response, 'text') else str(response.content)
                from src.utils.json_parser import safe_json_loads
                data = safe_json_loads(response_text)
                if not data:
                    raise ValueError(f'Failed to parse geocoding response: {json_err}')

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
        except httpx.RequestError as e:
            raise ValueError(f'Geocoding request failed: {e}')
        except httpx.HTTPStatusError as e:
            raise ValueError(f'Geocoding HTTP error: {e.response.status_code}')
        except (KeyError, IndexError) as e:
            raise ValueError(f'Invalid geocoding response format: {e}')
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
        Fetch comprehensive weather data including rainfall from Open-Meteo

        Args:
            location: City name or coordinates

        Returns:
            Dictionary with weather data including detailed rainfall information
        """
        try:
            # Step 1: Geocode the location
            coords = await self._geocode_location(location)

            # Step 2: Fetch comprehensive weather data from Open-Meteo
            # Including hourly and daily precipitation data
            response = await self.client.get(
                self.open_meteo_url,
                params={
                    'latitude': coords['latitude'],
                    'longitude': coords['longitude'],
                    'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,showers,snowfall,weather_code,wind_speed_10m,wind_direction_10m,pressure_msl',
                    'hourly': 'temperature_2m,relative_humidity_2m,precipitation,precipitation_probability,rain,showers,snowfall,weather_code,wind_speed_10m,wind_direction_10m',
                    'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,rain_sum,showers_sum,snowfall_sum,precipitation_hours,precipitation_probability_max,weather_code',
                    'timezone': 'auto',
                    'forecast_days': 7
                }
            )
            response.raise_for_status()

            # Safe JSON parsing with EOF error handling
            try:
                data = response.json()
            except (ValueError, json.JSONDecodeError) as json_err:
                # Try to parse response text directly
                response_text = response.text if hasattr(response, 'text') else str(response.content)
                from src.utils.json_parser import safe_json_loads
                data = safe_json_loads(response_text)
                if not data:
                    raise Exception(f'Failed to parse weather API response: {json_err}')

            if 'current' not in data or 'hourly' not in data:
                raise Exception('Invalid weather API response format')

            current = data['current']
            hourly = data['hourly']
            daily = data.get('daily', {})

            # Process hourly forecast (next 24 hours)
            hourly_forecast = []
            for i in range(min(24, len(hourly['time']))):
                hourly_forecast.append({
                    'datetime': hourly['time'][i],
                    'temp': hourly['temperature_2m'][i],
                    'description': self._get_weather_description(hourly['weather_code'][i]),
                    'humidity': hourly['relative_humidity_2m'][i],
                    'precipitation': hourly.get('precipitation', [0])[i] if i < len(hourly.get('precipitation', [])) else 0,
                    'precipitation_probability': hourly.get('precipitation_probability', [0])[i] if i < len(hourly.get('precipitation_probability', [])) else 0,
                    'rain': hourly.get('rain', [0])[i] if i < len(hourly.get('rain', [])) else 0,
                    'showers': hourly.get('showers', [0])[i] if i < len(hourly.get('showers', [])) else 0,
                    'snowfall': hourly.get('snowfall', [0])[i] if i < len(hourly.get('snowfall', [])) else 0,
                    'wind_speed': hourly.get('wind_speed_10m', [0])[i] if i < len(hourly.get('wind_speed_10m', [])) else 0
                })

            # Process daily forecast (next 7 days)
            daily_forecast = []
            if daily and 'time' in daily:
                for i in range(min(7, len(daily['time']))):
                    daily_forecast.append({
                        'date': daily['time'][i],
                        'temp_max': daily.get('temperature_2m_max', [0])[i] if i < len(daily.get('temperature_2m_max', [])) else 0,
                        'temp_min': daily.get('temperature_2m_min', [0])[i] if i < len(daily.get('temperature_2m_min', [])) else 0,
                        'precipitation_sum': daily.get('precipitation_sum', [0])[i] if i < len(daily.get('precipitation_sum', [])) else 0,
                        'rain_sum': daily.get('rain_sum', [0])[i] if i < len(daily.get('rain_sum', [])) else 0,
                        'showers_sum': daily.get('showers_sum', [0])[i] if i < len(daily.get('showers_sum', [])) else 0,
                        'snowfall_sum': daily.get('snowfall_sum', [0])[i] if i < len(daily.get('snowfall_sum', [])) else 0,
                        'precipitation_hours': daily.get('precipitation_hours', [0])[i] if i < len(daily.get('precipitation_hours', [])) else 0,
                        'precipitation_probability_max': daily.get('precipitation_probability_max', [0])[i] if i < len(daily.get('precipitation_probability_max', [])) else 0,
                        'weather_code': daily.get('weather_code', [0])[i] if i < len(daily.get('weather_code', [])) else 0,
                        'description': self._get_weather_description(daily.get('weather_code', [0])[i] if i < len(daily.get('weather_code', [])) else 0)
                    })

            # Calculate rainfall statistics
            current_precipitation = current.get('precipitation', 0)
            current_rain = current.get('rain', 0)
            current_showers = current.get('showers', 0)
            current_snowfall = current.get('snowfall', 0)
            
            # Total precipitation for today
            today_precipitation = sum([h.get('precipitation', 0) for h in hourly_forecast[:24]])
            today_rain = sum([h.get('rain', 0) for h in hourly_forecast[:24]])
            today_showers = sum([h.get('showers', 0) for h in hourly_forecast[:24]])
            
            # Next 24 hours precipitation forecast
            next_24h_precipitation = sum([h.get('precipitation', 0) for h in hourly_forecast])
            next_24h_rain = sum([h.get('rain', 0) for h in hourly_forecast])
            next_24h_showers = sum([h.get('showers', 0) for h in hourly_forecast])

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
                    'windDirection': current.get('wind_direction_10m', 0),
                    'precipitation': current_precipitation,
                    'rain': current_rain,
                    'showers': current_showers,
                    'snowfall': current_snowfall
                },
                'rainfall': {
                    'current': {
                        'precipitation': current_precipitation,
                        'rain': current_rain,
                        'showers': current_showers,
                        'snowfall': current_snowfall
                    },
                    'today': {
                        'total_precipitation': round(today_precipitation, 2),
                        'total_rain': round(today_rain, 2),
                        'total_showers': round(today_showers, 2),
                        'unit': 'mm'
                    },
                    'next_24h': {
                        'forecasted_precipitation': round(next_24h_precipitation, 2),
                        'forecasted_rain': round(next_24h_rain, 2),
                        'forecasted_showers': round(next_24h_showers, 2),
                        'unit': 'mm'
                    }
                },
                'hourly_forecast': hourly_forecast,
                'daily_forecast': daily_forecast,
                'source': 'Open-Meteo',
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            import traceback
            error_msg = str(e)
            # Don't print in production, just return error
            return {
                'success': False,
                'error': error_msg,
                'location': location,
                'message': f'Unable to fetch weather data for "{location}". {error_msg}'
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
            response = await self.client.get(
                f"{self.agriculture_api_url}/crop-data",
                params={
                    'location': location,
                    'crop': crop_type,
                    'api_key': self.agriculture_api_key
                }
            )
            response.raise_for_status()

            # Safe JSON parsing with EOF error handling
            try:
                data = response.json()
            except (ValueError, json.JSONDecodeError) as json_err:
                # Try to parse response text directly
                response_text = response.text if hasattr(response, 'text') else str(response.content)
                from src.utils.json_parser import safe_json_loads
                data = safe_json_loads(response_text)
                if not data:
                    import logging
                    logging.warning(f"Failed to parse agriculture API response: {json_err}")
                    return self._mock_agricultural_data(location, crop_type)

            return {
                'success': True,
                'location': location,
                'data': data,
                'timestamp': datetime.now().isoformat()
            }

        except httpx.RequestError as e:
            print(f"Agriculture API request error: {e}")
            return self._mock_agricultural_data(location, crop_type)
        except httpx.HTTPStatusError as e:
            print(f"Agriculture API HTTP error: {e.response.status_code}")
            return self._mock_agricultural_data(location, crop_type)
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

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
