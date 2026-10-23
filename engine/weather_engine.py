"""
AkshAI Weather Engine v1.0
==========================

Professional Weather + AQI + AkshAI Advice Engine.

Features:
- Live weather
- Temperature
- Feels-like temperature
- Humidity
- Wind speed/direction
- Rain / precipitation
- Rain probability
- Weather condition
- Sunrise / sunset
- Multi-day forecast
- AQI
- PM2.5 / PM10 / NO2 / O3 / SO2
- AQI category
- Professional AkshAI Advice
- Location search
- Natural-language weather queries
- Structured results
- Standard library only
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import json
import re


ENGINE_NAME = "AkshAI Weather Engine"
ENGINE_VERSION = "1.0"

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"


# ============================================================
# RESULT MODEL
# ============================================================

@dataclass
class WeatherResult:
    success: bool
    query: str

    location: str = ""
    country: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    timezone: str = ""

    temperature: Optional[float] = None
    feels_like: Optional[float] = None
    humidity: Optional[float] = None

    wind_speed: Optional[float] = None
    wind_direction: Optional[float] = None

    precipitation: Optional[float] = None
    rain: Optional[float] = None
    precipitation_probability: Optional[float] = None

    weather_code: Optional[int] = None
    weather_condition: str = ""

    sunrise: str = ""
    sunset: str = ""

    aqi: Optional[float] = None
    aqi_category: str = ""
    pm25: Optional[float] = None
    pm10: Optional[float] = None
    no2: Optional[float] = None
    o3: Optional[float] = None
    so2: Optional[float] = None

    advice: str = ""
    advice_points: List[str] = field(default_factory=list)

    forecast: List[Dict[str, Any]] = field(default_factory=list)

    formatted: str = ""

    source: str = "Open-Meteo"

    error: str = ""
    error_type: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "query": self.query,
            "location": self.location,
            "country": self.country,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timezone": self.timezone,
            "temperature": self.temperature,
            "feels_like": self.feels_like,
            "humidity": self.humidity,
            "wind_speed": self.wind_speed,
            "wind_direction": self.wind_direction,
            "precipitation": self.precipitation,
            "rain": self.rain,
            "precipitation_probability": self.precipitation_probability,
            "weather_code": self.weather_code,
            "weather_condition": self.weather_condition,
            "sunrise": self.sunrise,
            "sunset": self.sunset,
            "aqi": self.aqi,
            "aqi_category": self.aqi_category,
            "pm25": self.pm25,
            "pm10": self.pm10,
            "no2": self.no2,
            "o3": self.o3,
            "so2": self.so2,
            "advice": self.advice,
            "advice_points": self.advice_points,
            "forecast": self.forecast,
            "formatted": self.formatted,
            "source": self.source,
            "error": self.error,
            "error_type": self.error_type,
        }


# ============================================================
# WEATHER ENGINE
# ============================================================

class WeatherEngine:

    def __init__(self):

        self.engine_name = ENGINE_NAME
        self.version = ENGINE_VERSION

        self.temperature_unit = "celsius"
        self.wind_speed_unit = "kmh"
        self.timezone = "auto"

        self.http_timeout = 15

        self.weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",

            45: "Fog",
            48: "Depositing rime fog",

            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",

            56: "Light freezing drizzle",
            57: "Dense freezing drizzle",

            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",

            66: "Light freezing rain",
            67: "Heavy freezing rain",

            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",

            77: "Snow grains",

            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",

            85: "Slight snow showers",
            86: "Heavy snow showers",

            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail",
        }


    # ========================================================
    # HTTP
    # ========================================================

    def _get_json(
        self,
        url: str,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:

        query = urlencode(params, doseq=True)

        full_url = f"{url}?{query}"

        request = Request(
            full_url,
            headers={
                "User-Agent": "AkshAI/1.0"
            },
        )

        try:

            with urlopen(
                request,
                timeout=self.http_timeout,
            ) as response:

                data = response.read().decode("utf-8")

                return json.loads(data)

        except HTTPError as exc:

            raise RuntimeError(
                f"HTTP error {exc.code}"
            )

        except URLError as exc:

            raise RuntimeError(
                f"Network error: {exc.reason}"
            )

        except json.JSONDecodeError:

            raise RuntimeError(
                "Invalid JSON response."
            )


    # ========================================================
    # TEXT CLEANING
    # ========================================================

    def clean_text(self, value: Any) -> str:

        if value is None:
            return ""

        return " ".join(
            str(value).split()
        ).strip()


    # ========================================================
    # LOCATION SEARCH
    # ========================================================

    def geocode(
        self,
        location: str,
    ) -> Optional[Dict[str, Any]]:

        location = self.clean_text(location)

        if not location:
            return None

        params = {
            "name": location,
            "count": 1,
            "language": "en",
            "format": "json",
        }

        data = self._get_json(
            GEOCODING_URL,
            params,
        )

        results = data.get(
            "results",
            [],
        )

        if not results:
            return None

        result = results[0]

        return {
            "name": result.get("name", location),
            "country": result.get("country", ""),
            "latitude": result.get("latitude"),
            "longitude": result.get("longitude"),
            "timezone": result.get(
                "timezone",
                "UTC",
            ),
        }


    # ========================================================
    # WEATHER CONDITION
    # ========================================================

    def weather_condition(
        self,
        code: Optional[int],
    ) -> str:

        if code is None:
            return "Unknown"

        return self.weather_codes.get(
            int(code),
            "Unknown weather condition",
        )


    # ========================================================
    # AQI CATEGORY
    # ========================================================

    def aqi_category(
        self,
        aqi: Optional[float],
    ) -> str:

        if aqi is None:
            return "Unknown"

        if aqi <= 20:
            return "Good"

        if aqi <= 40:
            return "Fair"

        if aqi <= 60:
            return "Moderate"

        if aqi <= 80:
            return "Poor"

        if aqi <= 100:
            return "Very Poor"

        return "Extremely Poor"


    # ========================================================
    # AQI EMOJI
    # ========================================================

    def aqi_emoji(
        self,
        category: str,
    ) -> str:

        mapping = {
            "Good": "🟢",
            "Fair": "🟡",
            "Moderate": "🟠",
            "Poor": "🔴",
            "Very Poor": "🟣",
            "Extremely Poor": "⚫",
            "Unknown": "⚪",
        }

        return mapping.get(
            category,
            "⚪",
        )


    # ========================================================
    # WEATHER EMOJI
    # ========================================================

    def weather_emoji(
        self,
        code: Optional[int],
    ) -> str:

        if code is None:
            return "🌤️"

        code = int(code)

        if code == 0:
            return "☀️"

        if code in [1, 2]:
            return "🌤️"

        if code == 3:
            return "☁️"

        if code in [45, 48]:
            return "🌫️"

        if code in [51, 53, 55]:
            return "🌦️"

        if code in [56, 57]:
            return "🌧️"

        if code in [61, 63, 65]:
            return "🌧️"

        if code in [66, 67]:
            return "🌧️"

        if code in [71, 73, 75, 77]:
            return "❄️"

        if code in [80, 81, 82]:
            return "🌦️"

        if code in [85, 86]:
            return "🌨️"

        if code in [95, 96, 99]:
            return "⛈️"

        return "🌤️"


    # ========================================================
    # WIND DIRECTION
    # ========================================================

    def wind_direction_text(
        self,
        degrees: Optional[float],
    ) -> str:

        if degrees is None:
            return "Unknown"

        directions = [
            "N",
            "NNE",
            "NE",
            "ENE",
            "E",
            "ESE",
            "SE",
            "SSE",
            "S",
            "SSW",
            "SW",
            "WSW",
            "W",
            "WNW",
            "NW",
            "NNW",
        ]

        index = int(
            (degrees + 11.25) / 22.5
        ) % 16

        return directions[index]


    # ========================================================
    # AKSHAI ADVICE
    # ========================================================

    def generate_advice(
        self,
        result: WeatherResult,
    ) -> List[str]:

        advice = []

        temp = result.temperature
        feels = result.feels_like
        humidity = result.humidity
        rain_probability = result.precipitation_probability
        rain = result.rain
        wind = result.wind_speed

        aqi = result.aqi
        aqi_category = result.aqi_category

        code = result.weather_code

        # ----------------------------------------------------
        # Temperature
        # ----------------------------------------------------

        if temp is not None:

            if temp >= 40:
                advice.append(
                    "🥵 Temperature is extremely high. "
                    "Stay hydrated, avoid unnecessary outdoor activity "
                    "during peak heat, and prefer cool/shaded places."
                )

            elif temp >= 35:
                advice.append(
                    "☀️ It's quite hot today. "
                    "Keep water with you and avoid prolonged exposure "
                    "to direct sunlight."
                )

            elif temp >= 30:
                advice.append(
                    "💧 It's warm outside. "
                    "Regular hydration will help you stay comfortable."
                )

            elif temp <= 10:
                advice.append(
                    "🧥 It's quite cold. "
                    "Consider warm clothing if you're heading outdoors."
                )

        # ----------------------------------------------------
        # Feels like
        # ----------------------------------------------------

        if (
            feels is not None
            and temp is not None
            and feels - temp >= 4
        ):

            advice.append(
                "🌡️ It may feel warmer than the actual temperature "
                "because of humidity and other atmospheric conditions."
            )

        # ----------------------------------------------------
        # Humidity
        # ----------------------------------------------------

        if humidity is not None:

            if humidity >= 80:
                advice.append(
                    "💦 Humidity is high, so it may feel more uncomfortable "
                    "than the temperature suggests. Stay hydrated."
                )

            elif humidity <= 25:
                advice.append(
                    "🌬️ Air is relatively dry. "
                    "Keep yourself hydrated and stay comfortable indoors."
                )

        # ----------------------------------------------------
        # Rain
        # ----------------------------------------------------

        if (
            rain_probability is not None
            and rain_probability >= 70
        ):

            advice.append(
                "🌧️ There's a high chance of rain. "
                "Carrying an umbrella or suitable rain protection "
                "would be a smart choice."
            )

        elif (
            rain_probability is not None
            and rain_probability >= 40
        ):

            advice.append(
                "🌦️ Rain is possible today. "
                "If you're going out for a while, keeping an umbrella "
                "nearby could be useful."
            )

        if (
            rain is not None
            and rain >= 5
        ):

            advice.append(
                "☔ Rainfall may be significant, so allow some extra "
                "travel time and be careful around slippery areas."
            )

        # ----------------------------------------------------
        # Thunderstorm
        # ----------------------------------------------------

        if code in [95, 96, 99]:

            advice.append(
                "⛈️ Thunderstorm conditions are possible. "
                "If you're outdoors, move to a safe sheltered place "
                "when thunder or lightning becomes noticeable."
            )

        # ----------------------------------------------------
        # Wind
        # ----------------------------------------------------

        if wind is not None:

            if wind >= 40:
                advice.append(
                    "💨 Winds are strong. "
                    "Take extra care with outdoor activities and "
                    "avoid exposed or unstable areas."
                )

            elif wind >= 25:
                advice.append(
                    "🌬️ It's fairly windy today. "
                    "Keep lightweight belongings secure outdoors."
                )

        # ----------------------------------------------------
        # AQI
        # ----------------------------------------------------

        if aqi_category == "Good":

            advice.append(
                "🌿 Air quality is good. "
                "Outdoor activities should generally be comfortable."
            )

        elif aqi_category == "Fair":

            advice.append(
                "🌱 Air quality is fairly good. "
                "Most people can continue normal outdoor activities."
            )

        elif aqi_category == "Moderate":

            advice.append(
                "🟠 Air quality is moderate. "
                "If you are sensitive to air pollution, consider "
                "reducing prolonged outdoor exposure."
            )

        elif aqi_category == "Poor":

            advice.append(
                "🔴 Air quality is poor. "
                "Consider reducing prolonged or strenuous outdoor activity, "
                "especially if you are sensitive to pollution."
            )

        elif aqi_category == "Very Poor":

            advice.append(
                "🟣 Air quality is very poor. "
                "It's better to limit unnecessary outdoor exposure "
                "and avoid prolonged strenuous activity outside."
            )

        elif aqi_category == "Extremely Poor":

            advice.append(
                "⚫ Air quality is extremely poor. "
                "Avoid unnecessary outdoor exposure and follow local "
                "health guidance."
            )

        # ----------------------------------------------------
        # Final general advice
        # ----------------------------------------------------

        if not advice:

            advice.append(
                "✨ Conditions look fairly comfortable. "
                "Enjoy your day and stay prepared for normal changes."
            )

        return advice


    # ========================================================
    # FETCH WEATHER
    # ========================================================

    def fetch_weather(
        self,
        location: str,
        forecast_days: int = 7,
    ) -> WeatherResult:

        location = self.clean_text(location)

        if not location:

            return WeatherResult(
                success=False,
                query="",
                error="Location is required.",
                error_type="missing_location",
            )

        try:

            geo = self.geocode(location)

            if geo is None:

                return WeatherResult(
                    success=False,
                    query=location,
                    error=f"Location not found: {location}",
                    error_type="location_not_found",
                )

            latitude = float(
                geo["latitude"]
            )

            longitude = float(
                geo["longitude"]
            )

            timezone_name = geo.get(
                "timezone",
                "UTC",
            )

            # ------------------------------------------------
            # WEATHER API
            # ------------------------------------------------

            weather_params = {
                "latitude": latitude,
                "longitude": longitude,

                "current": ",".join([
                    "temperature_2m",
                    "relative_humidity_2m",
                    "apparent_temperature",
                    "precipitation",
                    "rain",
                    "weather_code",
                    "wind_speed_10m",
                    "wind_direction_10m",
                ]),

                "hourly": ",".join([
                    "precipitation_probability",
                    "precipitation",
                    "rain",
                    "temperature_2m",
                    "weather_code",
                ]),

                "daily": ",".join([
                    "weather_code",
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "apparent_temperature_max",
                    "apparent_temperature_min",
                    "precipitation_sum",
                    "precipitation_probability_max",
                    "sunrise",
                    "sunset",
                ]),

                "forecast_days": max(
                    1,
                    min(
                        int(forecast_days),
                        7,
                    ),
                ),

                "timezone": "auto",

                "temperature_unit": self.temperature_unit,

                "wind_speed_unit": self.wind_speed_unit,

                "precipitation_unit": "mm",
            }

            weather_data = self._get_json(
                WEATHER_URL,
                weather_params,
            )

            current = weather_data.get(
                "current",
                {},
            )

            daily = weather_data.get(
                "daily",
                {},
            )

            hourly = weather_data.get(
                "hourly",
                {},
            )

            weather_code = current.get(
                "weather_code"
            )

            result = WeatherResult(
                success=True,
                query=location,

                location=geo.get(
                    "name",
                    location,
                ),

                country=geo.get(
                    "country",
                    "",
                ),

                latitude=latitude,
                longitude=longitude,

                timezone=weather_data.get(
                    "timezone",
                    timezone_name,
                ),

                temperature=current.get(
                    "temperature_2m"
                ),

                feels_like=current.get(
                    "apparent_temperature"
                ),

                humidity=current.get(
                    "relative_humidity_2m"
                ),

                wind_speed=current.get(
                    "wind_speed_10m"
                ),

                wind_direction=current.get(
                    "wind_direction_10m"
                ),

                precipitation=current.get(
                    "precipitation"
                ),

                rain=current.get(
                    "rain"
                ),

                weather_code=weather_code,

                weather_condition=self.weather_condition(
                    weather_code
                ),

                source="Open-Meteo",
            )

            # ------------------------------------------------
            # HOURLY RAIN PROBABILITY
            # ------------------------------------------------

            probabilities = hourly.get(
                "precipitation_probability",
                [],
            )

            if probabilities:

                valid = [
                    x for x in probabilities[:3]
                    if isinstance(x, (int, float))
                ]

                if valid:

                    result.precipitation_probability = max(
                        valid
                    )

            # ------------------------------------------------
            # DAILY DATA
            # ------------------------------------------------

            dates = daily.get(
                "time",
                [],
            )

            max_temps = daily.get(
                "temperature_2m_max",
                [],
            )

            min_temps = daily.get(
                "temperature_2m_min",
                [],
            )

            daily_codes = daily.get(
                "weather_code",
                [],
            )

            daily_rain_probability = daily.get(
                "precipitation_probability_max",
                [],
            )

            sunrise = daily.get(
                "sunrise",
                [],
            )

            sunset = daily.get(
                "sunset",
                [],
            )

            rain_sum = daily.get(
                "precipitation_sum",
                [],
            )

            count = min(
                len(dates),
                len(max_temps),
                len(min_temps),
            )

            for index in range(count):

                item = {
                    "date": dates[index],
                    "max_temperature": max_temps[index],
                    "min_temperature": min_temps[index],
                    "weather_code": (
                        daily_codes[index]
                        if index < len(daily_codes)
                        else None
                    ),
                    "condition": self.weather_condition(
                        daily_codes[index]
                    )
                    if index < len(daily_codes)
                    else "Unknown",
                    "precipitation_probability": (
                        daily_rain_probability[index]
                        if index < len(
                            daily_rain_probability
                        )
                        else None
                    ),
                    "precipitation": (
                        rain_sum[index]
                        if index < len(rain_sum)
                        else None
                    ),
                    "sunrise": (
                        sunrise[index]
                        if index < len(sunrise)
                        else ""
                    ),
                    "sunset": (
                        sunset[index]
                        if index < len(sunset)
                        else ""
                    ),
                }

                result.forecast.append(item)

            if sunrise:
                result.sunrise = sunrise[0]

            if sunset:
                result.sunset = sunset[0]

            # ------------------------------------------------
            # AIR QUALITY
            # ------------------------------------------------

            air_params = {
                "latitude": latitude,
                "longitude": longitude,

                "current": ",".join([
                    "european_aqi",
                    "pm2_5",
                    "pm10",
                    "nitrogen_dioxide",
                    "ozone",
                    "sulphur_dioxide",
                ]),

                "timezone": "auto",
            }

            try:

                air_data = self._get_json(
                    AIR_QUALITY_URL,
                    air_params,
                )

                air_current = air_data.get(
                    "current",
                    {},
                )

                result.aqi = air_current.get(
                    "european_aqi"
                )

                result.pm25 = air_current.get(
                    "pm2_5"
                )

                result.pm10 = air_current.get(
                    "pm10"
                )

                result.no2 = air_current.get(
                    "nitrogen_dioxide"
                )

                result.o3 = air_current.get(
                    "ozone"
                )

                result.so2 = air_current.get(
                    "sulphur_dioxide"
                )

                result.aqi_category = self.aqi_category(
                    result.aqi
                )

            except Exception:

                result.aqi_category = "Unknown"

            # ------------------------------------------------
            # AKSHAI ADVICE
            # ------------------------------------------------

            result.advice_points = self.generate_advice(
                result
            )

            result.advice = "\n".join(
                f"• {point}"
                for point in result.advice_points
            )

            result.formatted = self.format_result(
                result
            )

            return result

        except Exception as exc:

            return WeatherResult(
                success=False,
                query=location,
                error=str(exc),
                error_type="weather_fetch_error",
            )
                # ========================================================
    # NATURAL QUERY
    # ========================================================

    def answer_query(
        self,
        query: Any,
    ) -> WeatherResult:

        query = self.clean_text(query)

        if not query:
            return WeatherResult(
                success=False,
                query="",
                error="Empty weather query.",
                error_type="empty_query",
            )

        location = query

        patterns = [
            r"what(?:'s| is)?\s+the\s+weather\s+(?:like\s+)?(?:in|at)\s+",
            r"weather\s+(?:in|at|of)\s+",
            r"temperature\s+(?:in|at|of)\s+",
            r"aqi\s+(?:in|at|of)\s+",
            r"air\s+quality\s+(?:in|at|of)\s+",
            r"forecast\s+(?:for|in|at)\s+",
        ]

        for pattern in patterns:
            location = re.sub(
                pattern,
                "",
                location,
                flags=re.IGNORECASE,
            )

        location = re.sub(
            r"\b(today|tomorrow|now|right now|please)\b",
            "",
            location,
            flags=re.IGNORECASE,
        )

        location = self.clean_text(location)

        if not location:
            location = "Delhi"

        return self.fetch_weather(location)


    # ========================================================
    # PROFESSIONAL FORMAT
    # ========================================================

    def format_result(
        self,
        result: WeatherResult,
    ) -> str:

        if not result.success:
            return (
                "❌ **Weather Update Unavailable**\n\n"
                f"{result.error}"
            )

        weather_icon = self.weather_emoji(
            result.weather_code
        )

        aqi_icon = self.aqi_emoji(
            result.aqi_category
        )

        lines = []

        lines.append(
            f"🌦️ **Weather Update — "
            f"{result.location}"
            f"{', ' + result.country if result.country else ''}**"
        )

        lines.append("")

        # Current conditions
        lines.append(
            f"{weather_icon} **Condition:** "
            f"{result.weather_condition}"
        )

        if result.temperature is not None:
            lines.append(
                f"🌡️ **Temperature:** "
                f"{result.temperature:.1f}°C"
            )

        if result.feels_like is not None:
            lines.append(
                f"🫠 **Feels Like:** "
                f"{result.feels_like:.1f}°C"
            )

        if result.humidity is not None:
            lines.append(
                f"💧 **Humidity:** "
                f"{result.humidity:.0f}%"
            )

        if result.wind_speed is not None:

            direction = self.wind_direction_text(
                result.wind_direction
            )

            lines.append(
                f"💨 **Wind:** "
                f"{result.wind_speed:.1f} km/h "
                f"({direction})"
            )

        if result.precipitation_probability is not None:
            lines.append(
                f"🌧️ **Rain Chance:** "
                f"{result.precipitation_probability:.0f}%"
            )

        # AQI
        lines.append("")
        lines.append("🌫️ **Air Quality**")

        if result.aqi is not None:
            lines.append(
                f"{aqi_icon} **AQI:** "
                f"{result.aqi:.0f} — "
                f"{result.aqi_category}"
            )

        if result.pm25 is not None:
            lines.append(
                f"• PM2.5: "
                f"{result.pm25:.1f} μg/m³"
            )

        if result.pm10 is not None:
            lines.append(
                f"• PM10: "
                f"{result.pm10:.1f} μg/m³"
            )

        if result.no2 is not None:
            lines.append(
                f"• NO₂: "
                f"{result.no2:.1f} μg/m³"
            )

        if result.o3 is not None:
            lines.append(
                f"• O₃: "
                f"{result.o3:.1f} μg/m³"
            )

        if result.so2 is not None:
            lines.append(
                f"• SO₂: "
                f"{result.so2:.1f} μg/m³"
            )

        # Sun information
        if result.sunrise or result.sunset:

            lines.append("")
            lines.append("🌅 **Sun Information**")

            if result.sunrise:
                lines.append(
                    f"🌅 Sunrise: "
                    f"{result.sunrise}"
                )

            if result.sunset:
                lines.append(
                    f"🌇 Sunset: "
                    f"{result.sunset}"
                )

        # Forecast
        if result.forecast:

            lines.append("")
            lines.append("📅 **Forecast**")

            for day in result.forecast[:7]:

                condition = day.get(
                    "condition",
                    "Unknown",
                )

                maximum = day.get(
                    "max_temperature"
                )

                minimum = day.get(
                    "min_temperature"
                )

                probability = day.get(
                    "precipitation_probability"
                )

                forecast_line = (
                    f"• **{day.get('date', '')}** — "
                    f"{condition}"
                )

                if minimum is not None:
                    forecast_line += (
                        f" | {minimum:.0f}°C"
                    )

                if maximum is not None:
                    forecast_line += (
                        f"–{maximum:.0f}°C"
                    )

                if probability is not None:
                    forecast_line += (
                        f" | 🌧️ {probability:.0f}%"
                    )

                lines.append(
                    forecast_line
                )

        # AkshAI Advice
        lines.append("")
        lines.append(
            "🤖 **AkshAI Advice**"
        )

        for point in result.advice_points:
            lines.append(point)

        lines.append("")
        lines.append(
            "💡 **AkshAI's Take:** "
            "Stay prepared, stay comfortable, "
            "and let the weather work around your plans. ✨"
        )

        lines.append("")
        lines.append(
            "📡 **Weather data:** Open-Meteo"
        )

        return "\n".join(lines)


    # ========================================================
    # STATUS
    # ========================================================

    def status(self) -> Dict[str, Any]:

        return {
            "engine": self.engine_name,
            "version": self.version,

            "weather_source": "Open-Meteo",

            "air_quality_source":
                "Open-Meteo Air Quality",

            "features": [
                "current weather",
                "temperature",
                "feels-like temperature",
                "humidity",
                "wind speed",
                "wind direction",
                "rain probability",
                "precipitation",
                "weather condition",
                "sunrise",
                "sunset",
                "daily forecast",
                "AQI",
                "PM2.5",
                "PM10",
                "NO2",
                "O3",
                "SO2",
                "AQI category",
                "professional AkshAI advice",
                "natural language queries",
            ],
        }


# ============================================================
# GLOBAL ENGINE
# ============================================================

_weather_engine = WeatherEngine()


# ============================================================
# PUBLIC FUNCTIONS
# ============================================================

def get_weather(
    location: str,
    forecast_days: int = 7,
) -> WeatherResult:

    return _weather_engine.fetch_weather(
        location,
        forecast_days,
    )


def answer_weather_query(
    query: Any,
) -> WeatherResult:

    return _weather_engine.answer_query(
        query
    )


def get_aqi(
    location: str,
) -> WeatherResult:

    return _weather_engine.fetch_weather(
        location,
        forecast_days=1,
    )


def weather_engine_status() -> Dict[str, Any]:

    return _weather_engine.status()


# ============================================================
# SELF TEST
# ============================================================

def run_self_test() -> None:

    print(f"{ENGINE_NAME} v{ENGINE_VERSION}")
    print("=" * 60)

    engine = WeatherEngine()

    passed = 0
    total = 0

    def test(
        name: str,
        condition: bool,
    ):

        nonlocal passed, total

        total += 1

        if condition:
            passed += 1
            print(f"{name} passed")
        else:
            print(f"{name} FAILED")

    # --------------------------------------------------------
    # Test 1
    # --------------------------------------------------------

    test(
        "Text cleaning test",
        engine.clean_text(
            "  Delhi   Weather  "
        ) == "Delhi Weather",
    )

    # --------------------------------------------------------
    # Test 2
    # --------------------------------------------------------

    test(
        "Weather code test",
        engine.weather_condition(0)
        == "Clear sky",
    )

    # --------------------------------------------------------
    # Test 3
    # --------------------------------------------------------

    test(
        "Rain code test",
        engine.weather_condition(61)
        == "Slight rain",
    )

    # --------------------------------------------------------
    # Test 4
    # --------------------------------------------------------

    test(
        "Weather emoji test",
        engine.weather_emoji(0)
        == "☀️",
    )

    # --------------------------------------------------------
    # Test 5
    # --------------------------------------------------------

    test(
        "AQI good test",
        engine.aqi_category(10)
        == "Good",
    )

    # --------------------------------------------------------
    # Test 6
    # --------------------------------------------------------

    test(
        "AQI poor test",
        engine.aqi_category(70)
        == "Poor",
    )

    # --------------------------------------------------------
    # Test 7
    # --------------------------------------------------------

    test(
        "AQI extreme test",
        engine.aqi_category(150)
        == "Extremely Poor",
    )

    # --------------------------------------------------------
    # Test 8
    # --------------------------------------------------------

    test(
        "AQI emoji test",
        engine.aqi_emoji("Good")
        == "🟢",
    )

    # --------------------------------------------------------
    # Test 9
    # --------------------------------------------------------

    test(
        "Wind direction test",
        engine.wind_direction_text(0)
        == "N",
    )

    # --------------------------------------------------------
    # Test 10
    # --------------------------------------------------------

    result = WeatherResult(
        success=True,
        query="Delhi",
        location="Delhi",
        temperature=32,
        feels_like=35,
        humidity=70,
        wind_speed=15,
        precipitation_probability=75,
        weather_code=61,
        weather_condition="Slight rain",
        aqi=75,
        aqi_category="Poor",
        pm25=35,
        pm10=60,
    )

    advice = engine.generate_advice(
        result
    )

    test(
        "AkshAI advice generation test",
        len(advice) >= 3,
    )

    # --------------------------------------------------------
    # Test 11
    # --------------------------------------------------------

    formatted = engine.format_result(
        result
    )

    test(
        "Professional formatting test",
        "AkshAI Advice" in formatted
        and "Weather Update" in formatted
        and "AQI" in formatted,
    )

    # --------------------------------------------------------
    # Test 12
    # --------------------------------------------------------

    empty = engine.answer_query("")

    test(
        "Empty query handling test",
        not empty.success
        and empty.error_type == "empty_query",
    )

    # --------------------------------------------------------
    # Test 13
    # --------------------------------------------------------

    missing = engine.fetch_weather("")

    test(
        "Missing location test",
        not missing.success
        and missing.error_type == "missing_location",
    )

    # --------------------------------------------------------
    # Test 14
    # --------------------------------------------------------

    status = engine.status()

    test(
        "Status test",
        status["engine"] == ENGINE_NAME
        and status["version"] == ENGINE_VERSION
        and "AQI" in status["features"],
    )

    # --------------------------------------------------------
    # Test 15
    # --------------------------------------------------------

    dictionary = result.to_dict()

    test(
        "Result dictionary test",
        dictionary["location"] == "Delhi"
        and dictionary["aqi"] == 75,
    )

    # --------------------------------------------------------
    # Test 16
    # --------------------------------------------------------

    hot_result = WeatherResult(
        success=True,
        query="Delhi",
        temperature=42,
        weather_code=0,
        weather_condition="Clear sky",
        aqi=10,
        aqi_category="Good",
    )

    hot_advice = engine.generate_advice(
        hot_result
    )

    test(
        "Hot weather advice test",
        any(
            "Temperature is extremely high"
            in item
            for item in hot_advice
        ),
    )

    # --------------------------------------------------------
    # Test 17
    # --------------------------------------------------------

    storm_result = WeatherResult(
        success=True,
        query="Delhi",
        temperature=28,
        weather_code=95,
        weather_condition="Thunderstorm",
        aqi=20,
        aqi_category="Good",
    )

    storm_advice = engine.generate_advice(
        storm_result
    )

    test(
        "Thunderstorm advice test",
        any(
            "Thunderstorm conditions"
            in item
            for item in storm_advice
        ),
    )

    # --------------------------------------------------------
    # Test 18
    # --------------------------------------------------------

    high_aqi_result = WeatherResult(
        success=True,
        query="Delhi",
        temperature=30,
        weather_code=0,
        weather_condition="Clear sky",
        aqi=120,
        aqi_category="Extremely Poor",
    )

    high_aqi_advice = engine.generate_advice(
        high_aqi_result
    )

    test(
        "AQI advice test",
        any(
            "extremely poor"
            in item.lower()
            for item in high_aqi_advice
        ),
    )

    # --------------------------------------------------------
    # Test 19
    # --------------------------------------------------------

    rain_result = WeatherResult(
        success=True,
        query="Delhi",
        temperature=30,
        weather_code=61,
        weather_condition="Slight rain",
        precipitation_probability=85,
        aqi=20,
        aqi_category="Good",
    )

    rain_advice = engine.generate_advice(
        rain_result
    )

    test(
        "Rain advice test",
        any(
            "umbrella"
            in item.lower()
            for item in rain_advice
        ),
    )

    # --------------------------------------------------------
    # Test 20
    # --------------------------------------------------------

    try:

        direction = engine.wind_direction_text(
            180
        )

        test(
            "Wind direction south test",
            direction == "S",
        )

    except Exception:

        test(
            "Wind direction south test",
            False,
        )

    print("-" * 60)
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print(
            "WEATHER ENGINE TEST PASSED ✅"
        )
    else:
        print(
            "WEATHER ENGINE TEST FAILED ❌"
        )


# ============================================================
# DIRECT RUN
# ============================================================

if __name__ == "__main__":
    run_self_test()            