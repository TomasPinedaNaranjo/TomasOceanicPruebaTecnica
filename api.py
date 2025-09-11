import requests

class MarsWeatherAPI:
    def __init__(self):
        self.api_key = "h7IawqkLYmSg0a5gz3dDCmEphEKe6jO9BLR2gePn"
        self.url = f"https://api.nasa.gov/insight_weather/?api_key={self.api_key}&feedtype=json&ver=1.0"
    
    def fetch_weather_data(self):
        """Obtiene datos meteorológicos de la API de la NASA"""
        try:
            print("🌍 Consultando API de la NASA...")
            response = requests.get(self.url)
            response.raise_for_status()
            data = response.json()
            
            print("✅ Datos obtenidos de la API")
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al consultar la API: {e}")
            return None
    
    def process_weather_data(self, api_data):
        """Procesa los datos de la API y los convierte a formato estructurado"""
        if not api_data:
            return None
        
        sol_keys = api_data.get("sol_keys", [])
        weather_data = {}
        
        print(f"📊 Procesando datos de {len(sol_keys)} sols...")
        
        for sol in sol_keys:
            sol_data = api_data[sol]
            
            # Extraer datos meteorológicos
            temp = sol_data.get("AT", {}).get("av")
            pressure = sol_data.get("PRE", {}).get("av")
            wind_speed = sol_data.get("HWS", {}).get("av")
            wind_dir = None
            
            if sol_data.get("WD", {}).get("most_common"):
                wind_dir = sol_data["WD"]["most_common"]["compass_point"]
            
            # Obtener fecha terrestre si está disponible
            earth_date = sol_data.get("First_UTC", "")
            
            weather_data[sol] = {
                'temperature': temp,
                'pressure': pressure,
                'wind_speed': wind_speed,
                'wind_direction': wind_dir,
                'earth_date': earth_date
            }
            
            print(f"Sol {sol}: Temp={temp}°C, Pressure={pressure} Pa, Wind={wind_speed} m/s, Dir={wind_dir}")
        
        return weather_data, api_data