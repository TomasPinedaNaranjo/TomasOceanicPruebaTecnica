import sqlite3
import json
from datetime import datetime

class MarsWeatherDB:
    def __init__(self, db_name="mars_weather.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Inicializa la base de datos y crea las tablas necesarias"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Crear tabla para datos meteorológicos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sol INTEGER UNIQUE NOT NULL,
                temperature REAL,
                pressure REAL,
                wind_speed REAL,
                wind_direction TEXT,
                earth_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Crear tabla para metadatos de la API
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_sols INTEGER,
                api_response TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"✅ Base de datos '{self.db_name}' inicializada correctamente")
    
    def save_weather_data(self, weather_data):
        """Guarda los datos meteorológicos en la base de datos"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            for sol, data in weather_data.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO weather_data 
                    (sol, temperature, pressure, wind_speed, wind_direction, earth_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    int(sol),
                    data.get('temperature'),
                    data.get('pressure'),
                    data.get('wind_speed'),
                    data.get('wind_direction'),
                    data.get('earth_date')
                ))
            
            conn.commit()
            print(f"✅ Datos meteorológicos guardados para {len(weather_data)} sols")
            
        except Exception as e:
            print(f"❌ Error al guardar datos: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def save_api_metadata(self, total_sols, api_response):
        """Guarda metadatos de la consulta a la API"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO api_metadata (total_sols, api_response)
                VALUES (?, ?)
            ''', (total_sols, json.dumps(api_response)))
            
            conn.commit()
            print("✅ Metadatos de API guardados")
            
        except Exception as e:
            print(f"❌ Error al guardar metadatos: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_all_weather_data(self):
        """Obtiene todos los datos meteorológicos guardados"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT sol, temperature, pressure, wind_speed, wind_direction, earth_date, created_at
            FROM weather_data
            ORDER BY sol DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_weather_by_sol(self, sol):
        """Obtiene datos meteorológicos de un sol específico"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT sol, temperature, pressure, wind_speed, wind_direction, earth_date, created_at
            FROM weather_data
            WHERE sol = ?
        ''', (sol,))
        
        result = cursor.fetchone()
        conn.close()
        return result
    
    def get_latest_weather(self):
        """Obtiene los datos meteorológicos más recientes"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT sol, temperature, pressure, wind_speed, wind_direction, earth_date, created_at
            FROM weather_data
            ORDER BY sol DESC
            LIMIT 1
        ''')
        
        result = cursor.fetchone()
        conn.close()
        return result
    
    def get_statistics(self):
        """Obtiene estadísticas básicas de los datos guardados"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_records,
                MIN(sol) as min_sol,
                MAX(sol) as max_sol,
                AVG(temperature) as avg_temp,
                AVG(pressure) as avg_pressure,
                AVG(wind_speed) as avg_wind_speed
            FROM weather_data
        ''')
        
        result = cursor.fetchone()
        conn.close()
        return result
    
    def display_saved_data(self):
        """Muestra los datos guardados en la base de datos"""
        print("\n📊 Datos guardados en la base de datos:")
        print("-" * 80)
        
        data = self.get_all_weather_data()
        
        if not data:
            print("No hay datos guardados en la base de datos.")
            return
        
        print(f"{'Sol':<6} {'Temp(°C)':<10} {'Pressure(Pa)':<12} {'Wind(m/s)':<10} {'Direction':<10} {'Fecha':<20}")
        print("-" * 80)
        
        for record in data:
            sol, temp, pressure, wind_speed, wind_dir, earth_date, created_at = record
            print(f"{sol:<6} {temp or 'N/A':<10} {pressure or 'N/A':<12} {wind_speed or 'N/A':<10} {wind_dir or 'N/A':<10} {earth_date[:10] if earth_date else 'N/A':<20}")
    
    def display_statistics(self):
        """Muestra estadísticas de los datos guardados"""
        print("\n📈 Estadísticas de los datos:")
        print("-" * 40)
        
        stats = self.get_statistics()
        if stats:
            total_records, min_sol, max_sol, avg_temp, avg_pressure, avg_wind_speed = stats
            print(f"Total de registros: {total_records}")
            print(f"Sols registrados: {min_sol} - {max_sol}")
            print(f"Temperatura promedio: {avg_temp:.2f}°C" if avg_temp else "Temperatura promedio: N/A")
            print(f"Presión promedio: {avg_pressure:.2f} Pa" if avg_pressure else "Presión promedio: N/A")
            print(f"Velocidad de viento promedio: {avg_wind_speed:.2f} m/s" if avg_wind_speed else "Velocidad de viento promedio: N/A")