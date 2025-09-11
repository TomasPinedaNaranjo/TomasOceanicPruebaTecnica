from api import MarsWeatherAPI
from bd import MarsWeatherDB
from ia import MarsAIChat 
from dotenv import load_dotenv
load_dotenv()

def ejecutar_proceso_completo():
    """Ejecuta el proceso completo: obtener datos de la API y guardarlos en BD"""
    print("🚀 Sistema de Monitoreo Meteorológico de Marte")
    print("=" * 50)
    
    # Crear instancias
    mars_api = MarsWeatherAPI()
    mars_db = MarsWeatherDB()
    
    # Obtener datos de la API
    api_data = mars_api.fetch_weather_data()
    
    if api_data:
        # Procesar datos
        result = mars_api.process_weather_data(api_data)
        
        if result:
            weather_data, raw_api_data = result
            
            # Guardar en base de datos
            mars_db.save_weather_data(weather_data)
            mars_db.save_api_metadata(len(weather_data), raw_api_data)
            
            # Mostrar datos guardados
            mars_db.display_saved_data()
            
            # Mostrar estadísticas
            mars_db.display_statistics()
    
    print("\n✅ Proceso completado!")

def menu_interactivo():
    """Menú interactivo para gestionar los datos"""
    mars_api = MarsWeatherAPI()
    mars_db = MarsWeatherDB()
    mars_ai = MarsAIChat()
    
    while True:
        print("\n🚀 Sistema de Monitoreo Meteorológico de Marte")
        print("=" * 50)
        print("1. Obtener y guardar datos de la NASA")
        print("2. Ver todos los datos guardados")
        print("3. Buscar datos por Sol específico")
        print("4. Ver datos más recientes")
        print("5. Ver estadísticas")
        print("6. Salir")
        print("7. Chat IA sobre los datos") 
        
        opcion = input("\nSelecciona una opción (1-7: ").strip()
        
        if opcion == "1":
            print("\n🌍 Obteniendo datos de la NASA...")
            api_data = mars_api.fetch_weather_data()
            if api_data:
                result = mars_api.process_weather_data(api_data)
                if result:
                    weather_data, raw_api_data = result
                    mars_db.save_weather_data(weather_data)
                    mars_db.save_api_metadata(len(weather_data), raw_api_data)
                    print("✅ Datos actualizados correctamente")
        
        elif opcion == "2":
            mars_db.display_saved_data()
        
        elif opcion == "3":
            try:
                sol = int(input("Ingresa el número de Sol a buscar: "))
                data = mars_db.get_weather_by_sol(sol)
                if data:
                    sol_num, temp, pressure, wind_speed, wind_dir, earth_date, created_at = data
                    print(f"\n📊 Datos del Sol {sol_num}:")
                    print(f"Temperatura: {temp}°C" if temp else "Temperatura: N/A")
                    print(f"Presión: {pressure} Pa" if pressure else "Presión: N/A")
                    print(f"Velocidad del viento: {wind_speed} m/s" if wind_speed else "Velocidad del viento: N/A")
                    print(f"Dirección del viento: {wind_dir}" if wind_dir else "Dirección del viento: N/A")
                    print(f"Fecha terrestre: {earth_date[:10] if earth_date else 'N/A'}")
                    print(f"Guardado el: {created_at}")
                else:
                    print(f"❌ No se encontraron datos para el Sol {sol}")
            except ValueError:
                print("❌ Por favor ingresa un número válido")
        
        elif opcion == "4":
            data = mars_db.get_latest_weather()
            if data:
                sol_num, temp, pressure, wind_speed, wind_dir, earth_date, created_at = data
                print(f"\n📊 Datos más recientes (Sol {sol_num}):")
                print(f"Temperatura: {temp}°C" if temp else "Temperatura: N/A")
                print(f"Presión: {pressure} Pa" if pressure else "Presión: N/A")
                print(f"Velocidad del viento: {wind_speed} m/s" if wind_speed else "Velocidad del viento: N/A")
                print(f"Dirección del viento: {wind_dir}" if wind_dir else "Dirección del viento: N/A")
                print(f"Fecha terrestre: {earth_date[:10] if earth_date else 'N/A'}")
                print(f"Guardado el: {created_at}")
            else:
                print("❌ No hay datos guardados")
        
        elif opcion == "5":
            mars_db.display_statistics()
        
        elif opcion == "6":
            print("👋 ¡Hasta luego!")
            break
            
        elif opcion == "7":
            print("\n🤖 Chat IA (DeepAI). Escribe 'salir' para terminar.")
            while True:
                q = input("Tu pregunta: ").strip()
                if not q or q.lower() == "salir":
                    break
                ans = mars_ai.ask(q)
                print(f"\nIA: {ans}\n")
        else:
            print("❌ Opción no válida. Por favor selecciona una opción del 1 al 6.")

if __name__ == "__main__":
    # Ejecutar proceso completo automáticamente
    ejecutar_proceso_completo()
    
    # Descomenta la siguiente línea si quieres usar el menú interactivo
    menu_interactivo()