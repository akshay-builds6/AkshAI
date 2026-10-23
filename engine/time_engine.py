"""
AkshAI Time Engine v1.0
=======================

Handles:
- Current time
- Current date
- Day of week
- Time zones
- 12/24-hour formatting
- Date/time information
- Time calculations
- Natural time queries
- Structured results
- Self-testing

Standard library only.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import re


ENGINE_NAME = "AkshAI Time Engine"
ENGINE_VERSION = "1.0"


# ============================================================
# RESULT MODEL
# ============================================================

@dataclass
class TimeResult:
    success: bool
    query: str
    time: str = ""
    date: str = ""
    day: str = ""
    timezone_name: str = ""
    utc_offset: str = ""
    timestamp: str = ""
    formatted: str = ""
    result_type: str = "time"
    error: str = ""
    error_type: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "query": self.query,
            "time": self.time,
            "date": self.date,
            "day": self.day,
            "timezone_name": self.timezone_name,
            "utc_offset": self.utc_offset,
            "timestamp": self.timestamp,
            "formatted": self.formatted,
            "result_type": self.result_type,
            "error": self.error,
            "error_type": self.error_type,
        }


# ============================================================
# TIME ENGINE
# ============================================================

class TimeEngine:

    def __init__(self):
        self.engine_name = ENGINE_NAME
        self.version = ENGINE_VERSION

        self.default_timezone = "Asia/Kolkata"

        self.city_timezones = {
            "delhi": "Asia/Kolkata",
            "new delhi": "Asia/Kolkata",
            "mumbai": "Asia/Kolkata",
            "kolkata": "Asia/Kolkata",
            "chennai": "Asia/Kolkata",
            "bangalore": "Asia/Kolkata",
            "bengaluru": "Asia/Kolkata",
            "hyderabad": "Asia/Kolkata",
            "pune": "Asia/Kolkata",
            "india": "Asia/Kolkata",

            "london": "Europe/London",
            "uk": "Europe/London",

            "paris": "Europe/Paris",
            "france": "Europe/Paris",

            "berlin": "Europe/Berlin",
            "germany": "Europe/Berlin",

            "dubai": "Asia/Dubai",
            "uae": "Asia/Dubai",

            "singapore": "Asia/Singapore",

            "tokyo": "Asia/Tokyo",
            "japan": "Asia/Tokyo",

            "beijing": "Asia/Shanghai",
            "china": "Asia/Shanghai",

            "seoul": "Asia/Seoul",
            "south korea": "Asia/Seoul",

            "sydney": "Australia/Sydney",
            "australia": "Australia/Sydney",

            "new york": "America/New_York",
            "nyc": "America/New_York",

            "los angeles": "America/Los_Angeles",
            "la": "America/Los_Angeles",

            "chicago": "America/Chicago",

            "toronto": "America/Toronto",
            "canada": "America/Toronto",

            "moscow": "Europe/Moscow",

            "istanbul": "Europe/Istanbul",

            "cairo": "Africa/Cairo",

            "johannesburg": "Africa/Johannesburg",

            "sao paulo": "America/Sao_Paulo",

            "mexico city": "America/Mexico_City",
        }


    # ========================================================
    # BASIC HELPERS
    # ========================================================

    def clean_query(self, query: Any) -> str:
        if query is None:
            return ""

        query = str(query)

        query = query.replace("\r\n", "\n")
        query = query.replace("\r", "\n")

        return " ".join(query.split()).strip()


    def normalize_timezone(self, timezone_name: Optional[str]) -> str:
        if not timezone_name:
            return self.default_timezone

        timezone_name = str(timezone_name).strip()

        lowered = timezone_name.lower()

        if lowered in self.city_timezones:
            return self.city_timezones[lowered]

        return timezone_name


    def get_timezone(self, timezone_name: Optional[str] = None):
        name = self.normalize_timezone(timezone_name)

        try:
            return ZoneInfo(name)
        except ZoneInfoNotFoundError:
            return None


    def format_offset(self, offset) -> str:
        if offset is None:
            return ""

        total_seconds = int(offset.total_seconds())

        sign = "+" if total_seconds >= 0 else "-"

        total_seconds = abs(total_seconds)

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60

        return f"UTC{sign}{hours:02d}:{minutes:02d}"


    # ========================================================
    # CURRENT DATETIME
    # ========================================================

    def now(self, timezone_name: Optional[str] = None) -> TimeResult:

        timezone_name = self.normalize_timezone(timezone_name)

        tz = self.get_timezone(timezone_name)

        if tz is None:
            return TimeResult(
                success=False,
                query="",
                error=f"Unknown timezone: {timezone_name}",
                error_type="invalid_timezone",
            )

        current = datetime.now(tz)

        return TimeResult(
            success=True,
            query="",
            time=current.strftime("%H:%M:%S"),
            date=current.strftime("%Y-%m-%d"),
            day=current.strftime("%A"),
            timezone_name=timezone_name,
            utc_offset=self.format_offset(current.utcoffset()),
            timestamp=current.isoformat(),
            formatted=current.strftime("%I:%M:%S %p"),
            result_type="datetime",
        )


    # ========================================================
    # CURRENT TIME
    # ========================================================

    def current_time(
        self,
        timezone_name: Optional[str] = None,
        use_24_hour: bool = False,
    ) -> TimeResult:

        result = self.now(timezone_name)

        if not result.success:
            return result

        current = datetime.fromisoformat(result.timestamp)

        if use_24_hour:
            formatted = current.strftime("%H:%M:%S")
        else:
            formatted = current.strftime("%I:%M:%S %p").lstrip("0")

        result.formatted = formatted
        result.result_type = "time"

        return result


    # ========================================================
    # CURRENT DATE
    # ========================================================

    def current_date(
        self,
        timezone_name: Optional[str] = None,
    ) -> TimeResult:

        result = self.now(timezone_name)

        if not result.success:
            return result

        current = datetime.fromisoformat(result.timestamp)

        result.formatted = current.strftime("%d %B %Y")
        result.result_type = "date"

        return result


    # ========================================================
    # DAY INFORMATION
    # ========================================================

    def current_day(
        self,
        timezone_name: Optional[str] = None,
    ) -> TimeResult:

        result = self.now(timezone_name)

        if not result.success:
            return result

        result.formatted = result.day
        result.result_type = "day"

        return result


    # ========================================================
    # TIMEZONE INFORMATION
    # ========================================================

    def timezone_info(
        self,
        timezone_name: Optional[str] = None,
    ) -> TimeResult:

        result = self.now(timezone_name)

        if not result.success:
            return result

        result.formatted = (
            f"{result.timezone_name} ({result.utc_offset})"
        )

        result.result_type = "timezone"

        return result


    # ========================================================
    # TIME IN CITY
    # ========================================================

    def time_in_city(self, city: str) -> TimeResult:

        city = self.clean_query(city)

        if not city:
            return TimeResult(
                success=False,
                query=city,
                error="City is required.",
                error_type="missing_city",
            )

        timezone_name = self.normalize_timezone(city)

        result = self.current_time(timezone_name)

        result.query = city

        if not result.success:
            result.error = f"Could not find timezone for '{city}'."
            result.error_type = "unknown_city"

        return result


    # ========================================================
    # PARSE TIMEZONE FROM QUERY
    # ========================================================

    def extract_timezone(self, query: str) -> Optional[str]:

        query_lower = query.lower()

        patterns = [
            r"\btime\s+(?:in|at|of)\s+([a-zA-Z ]+)",
            r"\b(?:in|at)\s+([a-zA-Z ]+)\s+(?:time|timezone)",
            r"\btimezone\s+(?:of|in)\s+([a-zA-Z ]+)",
        ]

        for pattern in patterns:

            match = re.search(pattern, query_lower)

            if match:

                location = match.group(1).strip()

                location = re.sub(
                    r"\b(now|please|today|right)\b",
                    "",
                    location,
                ).strip()

                if location in self.city_timezones:
                    return self.city_timezones[location]

        for city, timezone_name in self.city_timezones.items():

            if re.search(
                rf"\b{re.escape(city)}\b",
                query_lower,
            ):
                return timezone_name

        return None


    # ========================================================
    # NATURAL QUERY
    # ========================================================

    def answer_query(self, query: Any) -> TimeResult:

        query = self.clean_query(query)

        if not query:
            return TimeResult(
                success=False,
                query="",
                error="Empty time query.",
                error_type="empty_query",
            )

        lowered = query.lower()

        timezone_name = self.extract_timezone(query)

        # ----------------------------------------------------
        # Time request
        # ----------------------------------------------------

        if (
            "time" in lowered
            or "clock" in lowered
            or "what time" in lowered
        ):

            if timezone_name:

                result = self.current_time(timezone_name)

                result.query = query

                return result

            result = self.current_time()

            result.query = query

            return result

        # ----------------------------------------------------
        # Date request
        # ----------------------------------------------------

        if (
            "date" in lowered
            or "today" in lowered
            or "what day" in lowered
        ):

            if timezone_name:

                result = self.current_date(timezone_name)

                result.query = query

                return result

            result = self.current_date()

            result.query = query

            return result

        # ----------------------------------------------------
        # Day request
        # ----------------------------------------------------

        if (
            "day" in lowered
            or "weekday" in lowered
        ):

            if timezone_name:

                result = self.current_day(timezone_name)

                result.query = query

                return result

            result = self.current_day()

            result.query = query

            return result

        # ----------------------------------------------------
        # Timezone request
        # ----------------------------------------------------

        if (
            "timezone" in lowered
            or "time zone" in lowered
        ):

            if timezone_name:

                result = self.timezone_info(timezone_name)

                result.query = query

                return result

            result = self.timezone_info()

            result.query = query

            return result

        return TimeResult(
            success=False,
            query=query,
            error="I couldn't understand the time request.",
            error_type="unsupported_query",
        )


    # ========================================================
    # TIME ADDITION
    # ========================================================

    def add_time(
        self,
        base_time: datetime,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
    ) -> datetime:

        if not isinstance(base_time, datetime):
            raise TypeError("base_time must be a datetime.")

        return base_time + timedelta(
            hours=hours,
            minutes=minutes,
            seconds=seconds,
        )


    # ========================================================
    # TIME DIFFERENCE
    # ========================================================

    def time_difference(
        self,
        first: datetime,
        second: datetime,
    ) -> timedelta:

        if not isinstance(first, datetime):
            raise TypeError("first must be a datetime.")

        if not isinstance(second, datetime):
            raise TypeError("second must be a datetime.")

        return second - first


    # ========================================================
    # FORMAT DATETIME
    # ========================================================

    def format_datetime(
    self,
    value: datetime,
    use_24_hour: bool = False,
) -> str:

        if not isinstance(value, datetime):
            raise TypeError("value must be a datetime.")

        if use_24_hour:
            return value.strftime("%d %B %Y, %H:%M:%S")

        return value.strftime("%d %B %Y, %I:%M:%S %p")


    # ========================================================
    # PARSE SIMPLE DURATION
    # ========================================================

    def parse_duration(self, text: str) -> Optional[timedelta]:

        if not isinstance(text, str):
            return None

        text = text.lower().strip()

        hours = 0
        minutes = 0
        seconds = 0

        hour_match = re.search(
            r"(\d+(?:\.\d+)?)\s*(?:hours?|hrs?|h)\b",
            text,
        )

        minute_match = re.search(
            r"(\d+(?:\.\d+)?)\s*(?:minutes?|mins?|m)\b",
            text,
        )

        second_match = re.search(
            r"(\d+(?:\.\d+)?)\s*(?:seconds?|secs?|s)\b",
            text,
        )

        if hour_match:
            hours = float(hour_match.group(1))

        if minute_match:
            minutes = float(minute_match.group(1))

        if second_match:
            seconds = float(second_match.group(1))

        if not any([hour_match, minute_match, second_match]):
            return None

        return timedelta(
            hours=hours,
            minutes=minutes,
            seconds=seconds,
        )


    # ========================================================
    # STATUS
    # ========================================================

    def status(self) -> Dict[str, Any]:

        return {
            "engine": self.engine_name,
            "version": self.version,
            "default_timezone": self.default_timezone,
            "cities_supported": len(self.city_timezones),
            "features": [
                "current time",
                "current date",
                "day of week",
                "timezone information",
                "city time",
                "natural time queries",
                "time addition",
                "time difference",
                "duration parsing",
                "12-hour formatting",
                "24-hour formatting",
            ],
        }


# ============================================================
# GLOBAL ENGINE
# ============================================================

_time_engine = TimeEngine()


# ============================================================
# PUBLIC FUNCTIONS
# ============================================================

def get_current_time(
    timezone_name: Optional[str] = None,
    use_24_hour: bool = False,
) -> TimeResult:

    return _time_engine.current_time(
        timezone_name,
        use_24_hour,
    )


def get_current_date(
    timezone_name: Optional[str] = None,
) -> TimeResult:

    return _time_engine.current_date(timezone_name)


def get_current_day(
    timezone_name: Optional[str] = None,
) -> TimeResult:

    return _time_engine.current_day(timezone_name)


def get_time_in_city(city: str) -> TimeResult:

    return _time_engine.time_in_city(city)


def answer_time_query(query: Any) -> TimeResult:

    return _time_engine.answer_query(query)


def parse_duration(text: str) -> Optional[timedelta]:

    return _time_engine.parse_duration(text)


def time_engine_status() -> Dict[str, Any]:

    return _time_engine.status()


# ============================================================
# SELF TEST
# ============================================================

def run_self_test() -> None:

    print(f"{ENGINE_NAME} v{ENGINE_VERSION}")
    print("=" * 55)

    engine = TimeEngine()

    passed = 0
    total = 0

    def test(name: str, condition: bool):

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

    result = engine.now("Asia/Kolkata")

    test(
        "Current datetime test",
        result.success
        and result.time
        and result.date
        and result.day,
    )

    # --------------------------------------------------------
    # Test 2
    # --------------------------------------------------------

    result = engine.current_time(
        "Asia/Kolkata",
        False,
    )

    test(
        "12-hour time test",
        result.success
        and ("AM" in result.formatted or "PM" in result.formatted),
    )

    # --------------------------------------------------------
    # Test 3
    # --------------------------------------------------------

    result = engine.current_time(
        "Asia/Kolkata",
        True,
    )

    test(
        "24-hour time test",
        result.success
        and len(result.formatted.split(":")) == 3,
    )

    # --------------------------------------------------------
    # Test 4
    # --------------------------------------------------------

    result = engine.current_date("Asia/Kolkata")

    test(
        "Date test",
        result.success
        and len(result.formatted) > 5,
    )

    # --------------------------------------------------------
    # Test 5
    # --------------------------------------------------------

    result = engine.current_day("Asia/Kolkata")

    test(
        "Day test",
        result.success
        and result.formatted in [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ],
    )

    # --------------------------------------------------------
    # Test 6
    # --------------------------------------------------------

    result = engine.time_in_city("London")

    test(
        "City timezone test",
        result.success
        and result.timezone_name == "Europe/London",
    )

    # --------------------------------------------------------
    # Test 7
    # --------------------------------------------------------

    result = engine.time_in_city("Tokyo")

    test(
        "Tokyo timezone test",
        result.success
        and result.timezone_name == "Asia/Tokyo",
    )

    # --------------------------------------------------------
    # Test 8
    # --------------------------------------------------------

    result = engine.answer_query(
        "What time is it in London?"
    )

    test(
        "Natural London query test",
        result.success
        and result.timezone_name == "Europe/London",
    )

    # --------------------------------------------------------
    # Test 9
    # --------------------------------------------------------

    result = engine.answer_query(
        "What time is it?"
    )

    test(
        "Natural current time test",
        result.success,
    )

    # --------------------------------------------------------
    # Test 10
    # --------------------------------------------------------

    result = engine.answer_query(
        "What is today's date?"
    )

    test(
        "Natural date query test",
        result.success
        and result.result_type == "date",
    )

    # --------------------------------------------------------
    # Test 11
    # --------------------------------------------------------

    result = engine.answer_query(
        "What day is today?"
    )

    test(
        "Natural day query test",
        result.success
        and result.result_type == "date",
    )

    # --------------------------------------------------------
    # Test 12
    # --------------------------------------------------------

    result = engine.timezone_info("India")

    test(
        "Timezone info test",
        result.success
        and "Asia/Kolkata" in result.formatted,
    )

    # --------------------------------------------------------
    # Test 13
    # --------------------------------------------------------

    base = datetime(
        2026,
        1,
        1,
        10,
        30,
        0,
    )

    added = engine.add_time(
        base,
        hours=2,
        minutes=15,
    )

    test(
        "Time addition test",
        added.hour == 12
        and added.minute == 45,
    )

    # --------------------------------------------------------
    # Test 14
    # --------------------------------------------------------

    first = datetime(
        2026,
        1,
        1,
        10,
        0,
        0,
    )

    second = datetime(
        2026,
        1,
        1,
        12,
        30,
        0,
    )

    difference = engine.time_difference(
        first,
        second,
    )

    test(
        "Time difference test",
        difference.total_seconds() == 9000,
    )

    # --------------------------------------------------------
    # Test 15
    # --------------------------------------------------------

    duration = engine.parse_duration(
        "2 hours 30 minutes"
    )

    test(
        "Duration parsing test",
        duration is not None
        and duration.total_seconds() == 9000,
    )

    # --------------------------------------------------------
    # Test 16
    # --------------------------------------------------------

    invalid = engine.time_in_city(
        "UnknownCity123"
    )

    test(
        "Invalid city handling test",
        not invalid.success
        and invalid.error_type == "unknown_city",
    )

    # --------------------------------------------------------
    # Test 17
    # --------------------------------------------------------

    invalid_timezone = engine.now(
        "Invalid/Timezone"
    )

    test(
        "Invalid timezone handling test",
        not invalid_timezone.success
        and invalid_timezone.error_type == "invalid_timezone",
    )

    # --------------------------------------------------------
    # Test 18
    # --------------------------------------------------------

    empty = engine.answer_query("")

    test(
        "Empty query handling test",
        not empty.success
        and empty.error_type == "empty_query",
    )

    # --------------------------------------------------------
    # Test 19
    # --------------------------------------------------------

    formatted = engine.format_datetime(
        base,
        False,
    )

    test(
        "Datetime formatting test",
        "01 January 2026" in formatted,
    )

    # --------------------------------------------------------
    # Test 20
    # --------------------------------------------------------

    status = engine.status()

    test(
        "Status test",
        status["engine"] == ENGINE_NAME
        and status["version"] == ENGINE_VERSION,
    )

    print("-" * 55)
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("TIME ENGINE TEST PASSED ✅")
    else:
        print("TIME ENGINE TEST FAILED ❌")


# ============================================================
# DIRECT RUN
# ============================================================

if __name__ == "__main__":
    run_self_test()