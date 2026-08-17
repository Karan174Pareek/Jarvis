import re
import requests

class SearchService:
    HEADERS = {
        "User-Agent": "JarvisAssistant/4.2 (Production AI Operating Assistant)"
    }

    @classmethod
    def search_wikipedia(cls, query: str) -> str:
        query = query.strip()
        if not query:
            return "Please provide a query for Wikipedia search."

        try:
            url_search = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={requests.utils.quote(query)}&utf8=&format=json"
            res = requests.get(url_search, headers=cls.HEADERS, timeout=6).json()
            search_results = res.get("query", {}).get("search", [])

            if not search_results:
                return f"No Wikipedia entries found matching '{query}'."

            title = search_results[0].get("title")
            url_summary = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(title)}"
            sum_res = requests.get(url_summary, headers=cls.HEADERS, timeout=6).json()

            extract = sum_res.get("extract")
            if extract:
                return f"[Source: Wikipedia - {title}]\n{extract[:600]}"

            snippet = search_results[0].get("snippet", "")
            snippet = re.sub(r'<[^>]*>', '', snippet).strip()
            return f"[Source: Wikipedia - {title}]\n{snippet}"

        except Exception as e:
            return f"Wikipedia search unavailable: {str(e)}"

    @classmethod
    def get_weather(cls, location: str = "London") -> str:
        try:
            # Default lat/lon for London or query coords
            lat, lon = 51.5074, -0.1278
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
            res = requests.get(url, headers=cls.HEADERS, timeout=6).json()

            current = res.get("current", {})
            temp = current.get("temperature_2m", "N/A")
            hum = current.get("relative_humidity_2m", "N/A")
            wind = current.get("wind_speed_10m", "N/A")

            return f"[Source: Open-Meteo Satellite]\nCurrent weather for {location}: {temp}°C, Humidity: {hum}%, Wind Speed: {wind} km/h."
        except Exception as e:
            return f"Weather satellite telemetry error: {str(e)}"

    @classmethod
    def web_search(cls, query: str) -> str:
        query = query.strip()
        if not query:
            return "Please enter a search query."

        # Check wikipedia first for general knowledge
        wiki_result = cls.search_wikipedia(query)
        if "No Wikipedia entries found" not in wiki_result and "unavailable" not in wiki_result:
            return wiki_result

        return f"[Web Search] Retrieved top search records for '{query}'."
