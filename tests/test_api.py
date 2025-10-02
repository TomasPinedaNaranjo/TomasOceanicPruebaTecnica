import pytest
import requests
from unittest.mock import Mock, patch
import sys
import os

# Agregar el directorio padre al path para importar los módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import MarsWeatherAPI


class TestMarsWeatherAPI:
    """Pruebas unitarias para la clase MarsWeatherAPI"""
    
    def setup_method(self):
        """Configuración inicial para cada prueba"""
        self.api = MarsWeatherAPI()
    
    def test_init(self):
        """Prueba la inicialización de la clase"""
        assert self.api.api_key == "h7IawqkLYmSg0a5gz3dDCmEphEKe6jO9BLR2gePn"
        assert "api.nasa.gov" in self.api.url
        assert "insight_weather" in self.api.url
    
    @patch('requests.get')
    def test_fetch_weather_data_success(self, mock_get):
        """Prueba la obtención exitosa de datos de la API"""
        # Mock de respuesta exitosa
        mock_response = Mock()
        mock_response.json.return_value = {
            "sol_keys": ["100", "101"],
            "100": {
                "AT": {"av": -65.0},
                "PRE": {"av": 700.0},
                "HWS": {"av": 5.0},
                "WD": {"most_common": {"compass_point": "N"}},
                "First_UTC": "2023-01-01T00:00:00Z"
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.api.fetch_weather_data()
        
        assert result is not None
        assert "sol_keys" in result
        assert result["sol_keys"] == ["100", "101"]
        mock_get.assert_called_once_with(self.api.url)
    
    @patch('requests.get')
    def test_fetch_weather_data_network_error(self, mock_get):
        """Prueba el manejo de errores de red"""
        mock_get.side_effect = requests.exceptions.RequestException("Error de red")
        
        result = self.api.fetch_weather_data()
        
        assert result is None
    
    @patch('requests.get')
    def test_fetch_weather_data_http_error(self, mock_get):
        """Prueba el manejo de errores HTTP"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        result = self.api.fetch_weather_data()
        
        assert result is None
    
    def test_process_weather_data_none_input(self):
        """Prueba el procesamiento con entrada None"""
        result = self.api.process_weather_data(None)
        assert result is None
    
    def test_process_weather_data_empty_data(self):
        """Prueba el procesamiento con datos vacíos"""
        empty_data = {"sol_keys": []}
        result = self.api.process_weather_data(empty_data)
        assert result is not None
        weather_data, raw_data = result
        assert len(weather_data) == 0
        assert raw_data == empty_data
    
    def test_process_weather_data_valid_data(self):
        """Prueba el procesamiento con datos válidos"""
        test_data = {
            "sol_keys": ["100", "101"],
            "100": {
                "AT": {"av": -65.0},
                "PRE": {"av": 700.0},
                "HWS": {"av": 5.0},
                "WD": {"most_common": {"compass_point": "N"}},
                "First_UTC": "2023-01-01T00:00:00Z"
            },
            "101": {
                "AT": {"av": -70.0},
                "PRE": {"av": 720.0},
                "HWS": {"av": 7.0},
                "WD": {"most_common": {"compass_point": "S"}},
                "First_UTC": "2023-01-02T00:00:00Z"
            }
        }
        
        result = self.api.process_weather_data(test_data)
        assert result is not None
        
        weather_data, raw_data = result
        assert len(weather_data) == 2
        assert "100" in weather_data
        assert "101" in weather_data
        
        # Verificar datos del sol 100
        sol_100 = weather_data["100"]
        assert sol_100["temperature"] == -65.0
        assert sol_100["pressure"] == 700.0
        assert sol_100["wind_speed"] == 5.0
        assert sol_100["wind_direction"] == "N"
        assert sol_100["earth_date"] == "2023-01-01T00:00:00Z"
    
    def test_process_weather_data_missing_values(self):
        """Prueba el procesamiento con valores faltantes"""
        test_data = {
            "sol_keys": ["100"],
            "100": {
                "AT": {},  # Sin temperatura
                "PRE": {"av": 700.0},
                "HWS": {},  # Sin viento
                "WD": {},  # Sin dirección
                "First_UTC": "2023-01-01T00:00:00Z"
            }
        }
        
        result = self.api.process_weather_data(test_data)
        assert result is not None
        
        weather_data, raw_data = result
        sol_100 = weather_data["100"]
        assert sol_100["temperature"] is None
        assert sol_100["pressure"] == 700.0
        assert sol_100["wind_speed"] is None
        assert sol_100["wind_direction"] is None
        assert sol_100["earth_date"] == "2023-01-01T00:00:00Z"