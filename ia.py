import os
import requests
from bd import MarsWeatherDB

class MarsAIChat:
    def __init__(self, api_key: str | None = None, max_rows: int = 20, model: str | None = None, timeout: int = 60):
        # Clave y modelo desde .env o argumentos
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Falta la clave GEMINI_API_KEY. Ponla en .env o pásala al constructor.")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self.timeout = timeout

        self.db = MarsWeatherDB()
        self.max_rows = max_rows

        # Endpoint REST de Gemini (v1beta generateContent)
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.endpoint = f"{self.base_url}/models/{self.model}:generateContent"

    def _fetch_context(self) -> str:
        rows = self.db.get_all_weather_data()[:self.max_rows]
        stats = self.db.get_statistics()

        lines = []
        lines.append("Base de conocimiento: Meteorología de Marte (datos locales).")
        if rows:
            lines.append(f"- Registros totales mostrados: {min(len(rows), self.max_rows)} (ordenados por Sol desc).")
            lines.append("- Muestras recientes (Sol, Temp°C, Presión Pa, Viento m/s, Dirección, Fecha):")
            for r in rows:
                sol, temp, pressure, wind_speed, wind_dir, earth_date, _ = r
                lines.append(
                    f"  • Sol {sol}: Temp={temp if temp is not None else 'N/A'}, "
                    f"Presión={pressure if pressure is not None else 'N/A'}, "
                    f"Viento={wind_speed if wind_speed is not None else 'N/A'}, "
                    f"Dir={wind_dir if wind_dir else 'N/A'}, "
                    f"Fecha={earth_date[:10] if earth_date else 'N/A'}"
                )
        else:
            lines.append("- No hay datos meteorológicos guardados en la BD.")

        if stats:
            total_records, min_sol, max_sol, avg_temp, avg_pressure, avg_wind_speed = stats
            lines.append("Estadísticas:")
            lines.append(f"  • Total registros: {total_records}, Rango Sol: {min_sol} - {max_sol}")
            lines.append(f"  • Temp promedio: {round(avg_temp, 2) if avg_temp is not None else 'N/A'} °C")
            lines.append(f"  • Presión promedio: {round(avg_pressure, 2) if avg_pressure is not None else 'N/A'} Pa")
            lines.append(f"  • Viento promedio: {round(avg_wind_speed, 2) if avg_wind_speed is not None else 'N/A'} m/s")

        return "\n".join(lines)

    def ask(self, question: str) -> str:
        """
        Envía una pregunta a Gemini con contexto de la BD. Responde en español.
        """
        context = self._fetch_context()

        system_prompt = (
            "Eres un asistente que responde en español sobre meteorología de Marte usando SOLO "
            "la información del contexto proporcionado. Si algo no está en el contexto, indica "
            "claramente que no hay datos. Respuestas concisas y claras."
        )
        user_prompt = (
            f"Contexto:\n{context}\n\n"
            f"Pregunta: {question}\n"
            "Responde en español:"
        )
        # Para Gemini via REST, unimos prompts en un solo 'text'
        full_text = f"{system_prompt}\n\n{user_prompt}"

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": full_text}
                    ]
                }
            ],
            # Opcional: controlar generación
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 400
            }
        }

        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": self.api_key
        }

        try:
            resp = requests.post(self.endpoint, headers=headers, json=payload, timeout=self.timeout)
            # Manejo de errores HTTP explícito para mejor diagnóstico
            if resp.status_code == 429:
                return "Límite/cuota de Gemini superado (429). Revisa tu plan o intenta más tarde."
            if resp.status_code >= 400:
                # Intentar extraer mensaje de error del JSON
                try:
                    err = resp.json()
                except Exception:
                    err = {"error_text": resp.text[:300]}
                return f"Error al consultar Gemini ({resp.status_code}): {err}"

            data = resp.json()
            # Estructura típica: candidates[0].content.parts[*].text
            candidates = data.get("candidates") or []
            if not candidates:
                return "La IA no devolvió contenido."
            parts = candidates[0].get("content", {}).get("parts", [])
            texts = [p.get("text", "") for p in parts if isinstance(p, dict)]
            answer = "\n".join([t for t in texts if t]).strip()
            return answer if answer else "La IA no devolvió contenido."
        except requests.exceptions.RequestException as e:
            return f"Error de red al consultar Gemini: {e}"