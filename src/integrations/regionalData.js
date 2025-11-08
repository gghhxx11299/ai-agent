import axios from 'axios';
import { config } from '../../config/config.js';

class RegionalDataIntegration {
  constructor() {
    this.openMeteoUrl = 'https://api.open-meteo.com/v1/forecast';
    this.geocodingUrl = 'https://geocoding-api.open-meteo.com/v1/search';
    this.agricultureApiKey = config.agriculture.apiKey;
    this.agricultureApiUrl = config.agriculture.apiUrl;
  }

  /**
   * Geocode a location name to coordinates using Open-Meteo
   * @param {string} location - City name or location
   * @returns {Promise<Object>} - Coordinates and location info
   */
  async geocodeLocation(location) {
    try {
      const response = await axios.get(this.geocodingUrl, {
        params: {
          name: location,
          count: 1,
          language: 'en',
          format: 'json',
        },
        timeout: 10000,
      });

      if (!response.data.results || response.data.results.length === 0) {
        throw new Error(`Location "${location}" not found`);
      }

      const result = response.data.results[0];
      return {
        latitude: result.latitude,
        longitude: result.longitude,
        name: result.name,
        country: result.country,
        admin1: result.admin1, // State/region
      };
    } catch (error) {
      throw new Error(`Geocoding failed: ${error.message}`);
    }
  }

  /**
   * Get weather description from WMO code
   * @param {number} code - WMO weather code
   * @returns {string} - Human-readable description
   */
  getWeatherDescription(code) {
    const descriptions = {
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
    };
    return descriptions[code] || 'unknown';
  }

  /**
   * Fetch weather data for a location using Open-Meteo (free, no API key required)
   * @param {string} location - City name or coordinates
   * @returns {Promise<Object>} - Weather data
   */
  async getWeatherData(location) {
    try {
      // Step 1: Geocode the location
      const coords = await this.geocodeLocation(location);

      // Step 2: Fetch weather data from Open-Meteo
      const response = await axios.get(this.openMeteoUrl, {
        params: {
          latitude: coords.latitude,
          longitude: coords.longitude,
          current: 'temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,pressure_msl',
          hourly: 'temperature_2m,relative_humidity_2m,precipitation_probability,weather_code',
          timezone: 'auto',
          forecast_days: 3,
        },
        timeout: 15000,
      });

      const current = response.data.current;
      const hourly = response.data.hourly;

      // Get next 8 hours of forecast
      const forecastData = [];
      for (let i = 0; i < Math.min(8, hourly.time.length); i++) {
        forecastData.push({
          datetime: hourly.time[i],
          temp: hourly.temperature_2m[i],
          description: this.getWeatherDescription(hourly.weather_code[i]),
          humidity: hourly.relative_humidity_2m[i],
          precipitation: hourly.precipitation_probability[i] || 0,
        });
      }

      return {
        success: true,
        location: `${coords.name}, ${coords.country}`,
        coordinates: {
          latitude: coords.latitude,
          longitude: coords.longitude,
        },
        current: {
          temperature: current.temperature_2m,
          feelsLike: current.apparent_temperature,
          humidity: current.relative_humidity_2m,
          pressure: current.pressure_msl,
          description: this.getWeatherDescription(current.weather_code),
          windSpeed: current.wind_speed_10m,
          precipitation: current.precipitation,
        },
        forecast: forecastData,
        source: 'Open-Meteo',
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      console.error('Weather API error:', error.message);
      return {
        success: false,
        error: error.message,
        location,
        message: `Unable to fetch weather data for "${location}". ${error.message}`,
      };
    }
  }

  /**
   * Fetch agricultural data for a region
   * @param {string} location - Region name
   * @param {string} cropType - Type of crop (optional)
   * @returns {Promise<Object>} - Agricultural data
   */
  async getAgriculturalData(location, cropType = null) {
    if (!this.agricultureApiKey || !this.agricultureApiUrl) {
      console.warn('Agriculture API not configured.');
      return this.mockAgriculturalData(location, cropType);
    }

    try {
      const response = await axios.get(
        `${this.agricultureApiUrl}/crop-data`,
        {
          params: {
            location,
            crop: cropType,
            api_key: this.agricultureApiKey,
          },
          timeout: 10000,
        }
      );

      return {
        success: true,
        location,
        data: response.data,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      console.error('Agriculture API error:', error.message);
      return this.mockAgriculturalData(location, cropType);
    }
  }

  /**
   * Fetch satellite/earth observation data
   * @param {string} location - Location coordinates or name
   * @param {string} metric - Data metric (NDVI, rainfall, etc.)
   * @returns {Promise<Object>} - Satellite data
   */
  async getSatelliteData(location, metric = 'ndvi') {
    if (!config.gee.apiKey) {
      console.warn('Google Earth Engine API not configured.');
      return this.mockSatelliteData(location, metric);
    }

    // This is a placeholder - actual GEE integration would require
    // more complex authentication and API calls
    return this.mockSatelliteData(location, metric);
  }

  /**
   * Fetch soil data for a location
   * @param {string} location - Location name
   * @returns {Promise<Object>} - Soil data
   */
  async getSoilData(location) {
    // Mock implementation - integrate with real soil data API
    return {
      success: true,
      location,
      data: {
        soilType: 'Loamy',
        pH: 6.5,
        nitrogen: 'Medium',
        phosphorus: 'High',
        potassium: 'Medium',
        organicMatter: '3.2%',
        recommendations: [
          'Good drainage capacity',
          'Suitable for most crops',
          'Consider adding organic compost',
        ],
      },
      mock: true,
      timestamp: new Date().toISOString(),
    };
  }

  // Mock data methods for development/testing

  mockWeatherData(location) {
    return {
      success: true,
      location,
      current: {
        temperature: 25,
        feelsLike: 26,
        humidity: 65,
        pressure: 1013,
        description: 'partly cloudy',
        windSpeed: 3.5,
        precipitation: 0,
      },
      forecast: [
        { datetime: '2025-11-08T12:00', temp: 27, description: 'sunny', humidity: 60, precipitation: 10 },
        { datetime: '2025-11-08T15:00', temp: 28, description: 'clear sky', humidity: 58, precipitation: 5 },
        { datetime: '2025-11-08T18:00', temp: 24, description: 'few clouds', humidity: 70, precipitation: 15 },
      ],
      mock: true,
      message: 'Mock data - this should not appear when using Open-Meteo',
      timestamp: new Date().toISOString(),
    };
  }

  mockAgriculturalData(location, cropType) {
    return {
      success: true,
      location,
      cropType: cropType || 'general',
      data: {
        soilMoisture: 68,
        growingSeason: 'Active',
        recommendedCrops: ['Maize', 'Wheat', 'Sorghum'],
        alerts: [
          'Optimal planting conditions',
          'Monitor for pest activity',
        ],
        yieldForecast: 'Above average expected',
      },
      mock: true,
      message: 'Mock data - configure Agriculture API for real data',
      timestamp: new Date().toISOString(),
    };
  }

  mockSatelliteData(location, metric) {
    return {
      success: true,
      location,
      metric,
      data: {
        ndvi: 0.75,
        ndviTrend: 'increasing',
        vegetationHealth: 'Good',
        interpretation: 'Healthy vegetation cover detected',
      },
      mock: true,
      message: 'Mock data - configure GEE API for real satellite data',
      timestamp: new Date().toISOString(),
    };
  }
}

export default RegionalDataIntegration;
