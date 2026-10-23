"""
AkshAI - Formatter Engine
Version: 1.0
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import re


# ============================================================
# FORMAT RESULT
# ============================================================

@dataclass
class FormatResult:
    success: bool
    text: str
    format_type: str = "text"
    error: Optional[str] = None


# ============================================================
# EMOJI MAP
# ============================================================

EMOJI_MAP = {
    "hello": "👋",
    "greeting": "👋",
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "question": "❓",
    "idea": "💡",

    "ai": "🤖",
    "assistant": "🤖",
    "akshai": "🤖",
    "brain": "🧠",
    "conversation": "💬",
    "chat": "💬",

    "education": "📚",
    "study": "📖",
    "school": "🏫",
    "teacher": "👨‍🏫",
    "physics": "⚛️",
    "chemistry": "🧪",
    "maths": "📐",
    "mathematics": "📐",
    "jee": "🎯",
    "exam": "📝",
    "formula": "📌",

    "coding": "💻",
    "code": "💻",
    "python": "🐍",
    "programming": "👨‍💻",
    "developer": "👨‍💻",
    "bug": "🐛",
    "debug": "🔧",
    "file": "📄",
    "folder": "📁",

    "weather": "🌤️",
    "temperature": "🌡️",
    "rain": "🌧️",
    "cloud": "☁️",
    "sun": "☀️",
    "storm": "⛈️",
    "wind": "💨",
    "humidity": "💧",

    "time": "🕐",
    "clock": "⏰",
    "date": "📅",

    "calculator": "🧮",
    "calculation": "🧮",
    "search": "🔎",
    "internet": "🌐",
    "web": "🌐",
    "memory": "🧠",
    "notes": "🗒️",
    "profile": "👤",

    "money": "💰",
    "price": "💰",
    "shopping": "🛒",
    "food": "🍽️",
    "travel": "✈️",
    "location": "📍",
    "health": "❤️",
    "sports": "🏏",
    "cricket": "🏏",
    "football": "⚽",
}


# ============================================================
# FORMATTER ENGINE
# ============================================================

class FormatterEngine:

    def __init__(self):
        self.name = "Formatter Engine"
        self.version = "1.0"

    # ========================================================
    # TEXT CLEANING
    # ========================================================

    @staticmethod
    def clean_text(text: Any) -> str:

        if text is None:
            return ""

        text = str(text)

        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        lines = []

        for line in text.split("\n"):

            line = re.sub(
                r"[ \t]+",
                " ",
                line
            ).strip()

            lines.append(line)

        text = "\n".join(lines)

        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text
        )

        return text.strip()

    # ========================================================
    # EMOJI
    # ========================================================

    @staticmethod
    def emoji(name: str) -> str:

        if not name:
            return ""

        key = str(name).lower().strip()

        return EMOJI_MAP.get(key, "")

    # ========================================================
    # TOPIC DETECTION
    # ========================================================

    @staticmethod
    def detect_topic(text: Any) -> str:

        if text is None:
            return "general"

        text = str(text).lower()

        # ----------------------------------------------------
        # IMPORTANT:
        # Specific topics must be checked BEFORE broad topics.
        # ----------------------------------------------------

        # Python gets priority over generic coding.
        if re.search(r"\bpython\b", text):
            return "python"

        # Physics
        physics_keywords = [
            "physics",
            "force",
            "motion",
            "velocity",
            "acceleration",
            "energy",
            "momentum",
            "gravity",
            "बल",
            "गति"
        ]

        if any(
            keyword in text
            for keyword in physics_keywords
        ):
            return "physics"

        # Chemistry
        chemistry_keywords = [
            "chemistry",
            "chemical",
            "reaction",
            "atom",
            "molecule"
        ]

        if any(
            keyword in text
            for keyword in chemistry_keywords
        ):
            return "chemistry"

        # Maths
        maths_keywords = [
            "math",
            "maths",
            "mathematics",
            "equation",
            "algebra",
            "geometry",
            "calculus",
            "probability"
        ]

        if any(
            keyword in text
            for keyword in maths_keywords
        ):
            return "maths"

        # Weather
        weather_keywords = [
            "weather",
            "temperature",
            "rain",
            "humidity",
            "wind",
            "forecast",
            "बारिश",
            "मौसम",
            "तापमान"
        ]

        if any(
            keyword in text
            for keyword in weather_keywords
        ):
            return "weather"

        # Education
        education_keywords = [
            "school",
            "study",
            "exam",
            "homework",
            "teacher",
            "chapter",
            "class",
            "jee",
            "ncert"
        ]

        if any(
            keyword in text
            for keyword in education_keywords
        ):
            return "education"

        # Coding
        coding_keywords = [
            "coding",
            "code",
            "program",
            "programming",
            "function",
            "variable",
            "syntax",
            "bug",
            "debug",
            "developer"
        ]

        if any(
            keyword in text
            for keyword in coding_keywords
        ):
            return "coding"

        # Calculator
        calculator_keywords = [
            "calculate",
            "calculator",
            "plus",
            "minus",
            "multiply",
            "divide"
        ]

        if any(
            keyword in text
            for keyword in calculator_keywords
        ):
            return "calculator"

        # Time
        time_keywords = [
            "time",
            "clock",
            "date",
            "today",
            "tomorrow"
        ]

        if any(
            keyword in text
            for keyword in time_keywords
        ):
            return "time"

        # Search
        search_keywords = [
            "search",
            "internet",
            "web",
            "google",
            "online"
        ]

        if any(
            keyword in text
            for keyword in search_keywords
        ):
            return "search"

        # Memory
        memory_keywords = [
            "remember",
            "memory",
            "forget",
            "save"
        ]

        if any(
            keyword in text
            for keyword in memory_keywords
        ):
            return "memory"

        # Notes
        notes_keywords = [
            "note",
            "notes",
            "reminder",
            "todo"
        ]

        if any(
            keyword in text
            for keyword in notes_keywords
        ):
            return "notes"

        # Profile
        profile_keywords = [
            "profile",
            "about me",
            "my information"
        ]

        if any(
            keyword in text
            for keyword in profile_keywords
        ):
            return "profile"

        return "general"

    # ========================================================
    # AUTO EMOJI
    # ========================================================

    def auto_emoji(self, text: Any) -> str:

        topic = self.detect_topic(text)

        return self.emoji(topic)

    # ========================================================
    # HEADING
    # ========================================================

    def heading(
        self,
        text: Any,
        level: int = 2,
        add_emoji: bool = True
    ) -> str:

        text = self.clean_text(text)

        if not text:
            return ""

        if add_emoji:

            icon = self.auto_emoji(text)

            if icon:
                text = f"{icon} {text}"

        level = max(1, min(level, 6))

        return f"{'#' * level} {text}"

    # ========================================================
    # BULLET
    # ========================================================

    def bullet(
        self,
        text: Any,
        emoji: Optional[str] = None
    ) -> str:

        text = self.clean_text(text)

        if not text:
            return "-"

        if emoji:

            icon = self.emoji(emoji)

            if icon:
                return f"- {icon} {text}"

        return f"- {text}"

    # ========================================================
    # NUMBERED LIST
    # ========================================================

    def numbered_list(
        self,
        items: List[Any],
        start: int = 1
    ) -> str:

        if not items:
            return ""

        lines = []
        number = start

        for item in items:

            cleaned = self.clean_text(item)

            if not cleaned:
                continue

            lines.append(
                f"{number}. {cleaned}"
            )

            number += 1

        return "\n".join(lines)

    # ========================================================
    # BULLET LIST
    # ========================================================

    def bullet_list(
        self,
        items: List[Any],
        emoji: Optional[str] = None
    ) -> str:

        if not items:
            return ""

        lines = []

        for item in items:

            cleaned = self.clean_text(item)

            if not cleaned:
                continue

            if emoji:

                icon = self.emoji(emoji)

                if icon:
                    lines.append(
                        f"- {icon} {cleaned}"
                    )
                    continue

            lines.append(
                f"- {cleaned}"
            )

        return "\n".join(lines)

    # ========================================================
    # KEY VALUE
    # ========================================================

    def key_value(
        self,
        data: Dict[str, Any],
        separator: str = ": "
    ) -> str:

        if not isinstance(data, dict):
            return ""

        lines = []

        for key, value in data.items():

            key_text = self.clean_text(key)
            value_text = self.clean_text(value)

            if not key_text:
                continue

            lines.append(
                f"**{key_text}**{separator}{value_text}"
            )

        return "\n".join(lines)

    # ========================================================
    # TABLE
    # ========================================================

    def table(
        self,
        headers: List[Any],
        rows: List[List[Any]]
    ) -> str:

        if not headers:
            return ""

        cleaned_headers = [
            self.clean_text(item)
            for item in headers
        ]

        header_line = (
            "| "
            + " | ".join(cleaned_headers)
            + " |"
        )

        separator_line = (
            "| "
            + " | ".join(
                ["---"] * len(cleaned_headers)
            )
            + " |"
        )

        lines = [
            header_line,
            separator_line
        ]

        for row in rows:

            if not isinstance(row, (list, tuple)):
                continue

            cleaned_row = [
                self.clean_text(item)
                for item in row
            ]

            while len(cleaned_row) < len(cleaned_headers):
                cleaned_row.append("")

            cleaned_row = cleaned_row[
                :len(cleaned_headers)
            ]

            lines.append(
                "| "
                + " | ".join(cleaned_row)
                + " |"
            )

        return "\n".join(lines)

    # ========================================================
    # CODE BLOCK
    # ========================================================

    def code_block(
        self,
        code: Any,
        language: str = ""
    ) -> str:

        if code is None:
            return ""

        code = str(code)

        language = (
            str(language).strip().lower()
            if language
            else ""
        )

        return (
            f"```{language}\n"
            f"{code.rstrip()}\n"
            f"```"
        )

    # ========================================================
    # CALCULATOR FORMAT
    # ========================================================

    def format_calculation(
        self,
        expression: Any,
        result: Any,
        unit: Optional[str] = None
    ) -> str:

        expression = self.clean_text(expression)
        result = self.clean_text(result)

        lines = [
            "🧮 **Calculation**"
        ]

        if expression:

            lines.append(
                f"**Expression:** `{expression}`"
            )

        if unit:

            unit = self.clean_text(unit)

            lines.append(
                f"**Result:** {result} {unit}"
            )

        else:

            lines.append(
                f"**Result:** {result}"
            )

        return "\n".join(lines)

    # ========================================================
    # WEATHER FORMAT
    # ========================================================

    def format_weather(
        self,
        weather: Dict[str, Any]
    ) -> str:

        if not isinstance(weather, dict):
            return self.clean_text(weather)

        lines = []

        location = weather.get(
            "location",
            weather.get("city", "")
        )

        condition = weather.get(
            "condition",
            weather.get("description", "")
        )

        temperature = weather.get(
            "temperature",
            weather.get("temp", "")
        )

        humidity = weather.get(
            "humidity",
            ""
        )

        wind = weather.get(
            "wind",
            weather.get("wind_speed", "")
        )

        rain = weather.get(
            "rain_probability",
            weather.get("rain_chance", "")
        )

        title = "🌤️ **Weather Update**"

        if location:

            title += (
                f" — {self.clean_text(location)}"
            )

        lines.append(title)

        if temperature != "":
            lines.append(
                f"🌡️ **Temperature:** {temperature}"
            )

        if condition:

            lines.append(
                f"☁️ **Condition:** "
                f"{self.clean_text(condition)}"
            )

        if humidity != "":

            lines.append(
                f"💧 **Humidity:** {humidity}"
            )

        if wind != "":

            lines.append(
                f"💨 **Wind:** {wind}"
            )

        if rain != "":

            lines.append(
                f"🌧️ **Rain probability:** {rain}"
            )

        advice = weather.get(
            "AkshAI Advice",
            weather.get("advice", "")
        )

        if advice:

            lines.append("")

            lines.append(
                "💡 **AkshAI Advice**"
            )

            lines.append(
                self.clean_text(advice)
            )

        return "\n".join(lines)

    # ========================================================
    # SEARCH RESULT FORMAT
    # ========================================================

    def format_search_result(
        self,
        results: Any
    ) -> str:

        if results is None:
            return "🔎 **Search:** No results found."

        if isinstance(results, dict):

            title = results.get(
                "title",
                "Search Result"
            )

            snippet = results.get(
                "snippet",
                results.get(
                    "description",
                    ""
                )
            )

            url = results.get(
                "url",
                ""
            )

            lines = [
                f"🔎 **{self.clean_text(title)}**"
            ]

            if snippet:

                lines.append(
                    self.clean_text(snippet)
                )

            if url:

                lines.append(
                    f"🔗 {self.clean_text(url)}"
                )

            return "\n".join(lines)

        if isinstance(results, list):

            lines = [
                "🔎 **Search Results**"
            ]

            for index, item in enumerate(
                results,
                start=1
            ):

                if isinstance(item, dict):

                    title = self.clean_text(
                        item.get(
                            "title",
                            f"Result {index}"
                        )
                    )

                    snippet = self.clean_text(
                        item.get(
                            "snippet",
                            item.get(
                                "description",
                                ""
                            )
                        )
                    )

                    lines.append(
                        f"{index}. **{title}**"
                    )

                    if snippet:

                        lines.append(
                            f"   {snippet}"
                        )

                else:

                    lines.append(
                        f"{index}. "
                        f"{self.clean_text(item)}"
                    )

            return "\n".join(lines)

        return self.clean_text(results)

    # ========================================================
    # SUCCESS
    # ========================================================

    def success(
        self,
        message: Any
    ) -> str:

        return (
            f"✅ {self.clean_text(message)}"
        )

    # ========================================================
    # ERROR
    # ========================================================

    def error(
        self,
        message: Any
    ) -> str:

        return (
            f"❌ {self.clean_text(message)}"
        )

    # ========================================================
    # WARNING
    # ========================================================

    def warning(
        self,
        message: Any
    ) -> str:

        return (
            f"⚠️ {self.clean_text(message)}"
        )

    # ========================================================
    # INFO
    # ========================================================

    def info(
        self,
        message: Any
    ) -> str:

        return (
            f"ℹ️ {self.clean_text(message)}"
        )

    # ========================================================
    # FORMAT DATA
    # ========================================================

    def format_data(
        self,
        data: Any
    ) -> str:

        if data is None:
            return ""

        if isinstance(data, str):
            return self.clean_text(data)

        if isinstance(data, dict):
            return self.key_value(data)

        if isinstance(data, (list, tuple)):

            return self.bullet_list(
                list(data)
            )

        return self.clean_text(data)

    # ========================================================
    # SMART FORMAT
    # ========================================================

    def smart_format(
        self,
        data: Any,
        format_type: Optional[str] = None
    ) -> FormatResult:

        try:

            if format_type:

                format_type = (
                    str(format_type)
                    .lower()
                    .strip()
                )

            # Explicit calculation
            if format_type == "calculation":

                if isinstance(data, dict):

                    text = self.format_calculation(
                        data.get(
                            "expression",
                            ""
                        ),
                        data.get(
                            "result",
                            ""
                        ),
                        data.get(
                            "unit",
                            None
                        )
                    )

                else:

                    text = self.clean_text(data)

                return FormatResult(
                    True,
                    text,
                    "calculation"
                )

            # Explicit weather
            if format_type == "weather":

                text = self.format_weather(
                    data
                )

                return FormatResult(
                    True,
                    text,
                    "weather"
                )

            # Explicit search
            if format_type == "search":

                text = self.format_search_result(
                    data
                )

                return FormatResult(
                    True,
                    text,
                    "search"
                )

            # Explicit code
            if format_type == "code":

                text = self.code_block(
                    data
                )

                return FormatResult(
                    True,
                    text,
                    "code"
                )

            # Automatic dictionary detection
            if isinstance(data, dict):

                weather_keys = {
                    "temperature",
                    "temp",
                    "condition",
                    "humidity",
                    "wind",
                    "rain_probability",
                    "rain_chance"
                }

                if weather_keys.intersection(
                    data.keys()
                ):

                    text = self.format_weather(
                        data
                    )

                    return FormatResult(
                        True,
                        text,
                        "weather"
                    )

                search_keys = {
                    "title",
                    "snippet",
                    "url"
                }

                if search_keys.intersection(
                    data.keys()
                ):

                    text = self.format_search_result(
                        data
                    )

                    return FormatResult(
                        True,
                        text,
                        "search"
                    )

            text = self.format_data(data)

            return FormatResult(
                True,
                text,
                "text"
            )

        except Exception as exc:

            return FormatResult(
                False,
                "",
                "error",
                str(exc)
            )

    # ========================================================
    # STATUS
    # ========================================================

    def get_status(self) -> Dict[str, Any]:

        return {
            "engine": self.name,
            "version": self.version,
            "status": "ready",
            "features": [
                "text_cleaning",
                "emoji_mapping",
                "topic_detection",
                "auto_emoji",
                "headings",
                "bullets",
                "numbered_lists",
                "key_value",
                "tables",
                "code_blocks",
                "calculator_formatting",
                "weather_formatting",
                "search_formatting",
                "success_messages",
                "error_messages",
                "warning_messages",
                "info_messages",
                "smart_formatting",
            ]
        }


# ============================================================
# GLOBAL FORMATTER
# ============================================================

formatter_engine = FormatterEngine()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def format_text(text: Any) -> str:
    return formatter_engine.clean_text(text)


def add_emoji(
    text: Any,
    emoji_name: Optional[str] = None
) -> str:

    text = formatter_engine.clean_text(text)

    if not text:
        return ""

    if emoji_name:

        icon = formatter_engine.emoji(
            emoji_name
        )

    else:

        icon = formatter_engine.auto_emoji(
            text
        )

    if icon:
        return f"{icon} {text}"

    return text


def make_heading(
    text: Any,
    level: int = 2
) -> str:

    return formatter_engine.heading(
        text,
        level
    )


def make_bullets(
    items: List[Any]
) -> str:

    return formatter_engine.bullet_list(
        items
    )


def make_numbered_list(
    items: List[Any]
) -> str:

    return formatter_engine.numbered_list(
        items
    )


def format_calculation(
    expression: Any,
    result: Any,
    unit: Optional[str] = None
) -> str:

    return formatter_engine.format_calculation(
        expression,
        result,
        unit
    )


def format_weather(
    weather: Dict[str, Any]
) -> str:

    return formatter_engine.format_weather(
        weather
    )


def format_search_result(
    results: Any
) -> str:

    return formatter_engine.format_search_result(
        results
    )


# ============================================================
# SELF TEST
# ============================================================

def run_formatter_test() -> bool:

    engine = FormatterEngine()

    # --------------------------------------------------------
    # Text cleaning
    # --------------------------------------------------------

    cleaned = engine.clean_text(
        "  Hello     AkshAI   \n\n\n  World  "
    )

    if cleaned != "Hello AkshAI\n\nWorld":

        print("FAILED text cleaning")
        return False

    print("Text cleaning test passed")

    # --------------------------------------------------------
    # Emoji mapping
    # --------------------------------------------------------

    if engine.emoji("python") != "🐍":

        print("FAILED emoji mapping")
        return False

    if engine.emoji("physics") != "⚛️":

        print("FAILED emoji mapping")
        return False

    print("Emoji mapping tests passed")

    # --------------------------------------------------------
    # Topic detection
    # --------------------------------------------------------

    if engine.detect_topic(
        "Explain Newton's law in physics"
    ) != "physics":

        print("FAILED topic detection")
        return False

    if engine.detect_topic(
        "Show me today's weather"
    ) != "weather":

        print("FAILED topic detection")
        return False

    print("Topic detection tests passed")

    # --------------------------------------------------------
    # Auto emoji
    # --------------------------------------------------------

    if engine.auto_emoji(
        "Write Python code"
    ) != "🐍":

        print("FAILED auto emoji")
        return False

    print("Auto emoji test passed")

    # --------------------------------------------------------
    # Heading
    # --------------------------------------------------------

    heading = engine.heading(
        "Physics",
        level=2
    )

    if not heading.startswith("##"):

        print("FAILED heading")
        return False

    print("Heading test passed")

    # --------------------------------------------------------
    # Bullet
    # --------------------------------------------------------

    bullet = engine.bullet(
        "Learn Python"
    )

    if bullet != "- Learn Python":

        print("FAILED bullet")
        return False

    print("Bullet test passed")

    # --------------------------------------------------------
    # Numbered list
    # --------------------------------------------------------

    numbered = engine.numbered_list(
        [
            "First",
            "Second",
            "Third"
        ]
    )

    if numbered != (
        "1. First\n"
        "2. Second\n"
        "3. Third"
    ):

        print("FAILED numbered list")
        return False

    print("Numbered list test passed")

    # --------------------------------------------------------
    # Bullet list
    # --------------------------------------------------------

    bullets = engine.bullet_list(
        [
            "One",
            "Two"
        ]
    )

    if bullets != "- One\n- Two":

        print("FAILED bullet list")
        return False

    print("Bullet list test passed")

    # --------------------------------------------------------
    # Key value
    # --------------------------------------------------------

    key_value = engine.key_value(
        {
            "Name": "AkshAI",
            "Version": "1.0"
        }
    )

    if (
        "**Name**: AkshAI" not in key_value
        or
        "**Version**: 1.0" not in key_value
    ):

        print("FAILED key-value")
        return False

    print("Key-value test passed")

    # --------------------------------------------------------
    # Table
    # --------------------------------------------------------

    table = engine.table(
        ["Name", "Age"],
        [
            ["AkshAI", "1.0"],
            ["Test", "2"]
        ]
    )

    if "| Name | Age |" not in table:

        print("FAILED table")
        return False

    print("Table test passed")

    # --------------------------------------------------------
    # Code block
    # --------------------------------------------------------

    code = engine.code_block(
        "print('Hello')",
        "python"
    )

    if "```python" not in code:

        print("FAILED code block")
        return False

    print("Code block test passed")

    # --------------------------------------------------------
    # Calculator formatting
    # --------------------------------------------------------

    calc = engine.format_calculation(
        "25 + 25",
        "50"
    )

    if "50" not in calc:

        print("FAILED calculator formatting")
        return False

    print("Calculator formatting test passed")

    # --------------------------------------------------------
    # Weather formatting
    # --------------------------------------------------------

    weather = engine.format_weather(
        {
            "location": "Delhi",
            "temperature": "30°C",
            "condition": "Clear",
            "humidity": "60%",
            "wind": "10 km/h",
            "rain_probability": "20%",
            "AkshAI Advice": "Carry water."
        }
    )

    if "Delhi" not in weather:

        print("FAILED weather formatting")
        return False

    if "AkshAI Advice" not in weather:

        print("FAILED weather advice")
        return False

    print("Weather formatting test passed")

    # --------------------------------------------------------
    # Search formatting
    # --------------------------------------------------------

    search = engine.format_search_result(
        {
            "title": "AkshAI",
            "snippet": "AI assistant project.",
            "url": "https://example.com"
        }
    )

    if "AkshAI" not in search:

        print("FAILED search formatting")
        return False

    print("Search formatting test passed")

    # --------------------------------------------------------
    # Status
    # --------------------------------------------------------

    status = engine.get_status()

    if status.get("status") != "ready":

        print("FAILED status")
        return False

    print("Status test passed")

    # --------------------------------------------------------
    # Smart formatting
    # --------------------------------------------------------

    smart = engine.smart_format(
        {
            "temperature": "30°C",
            "condition": "Sunny",
            "humidity": "50%"
        }
    )

    if not smart.success:

        print("FAILED smart formatting")
        return False

    if smart.format_type != "weather":

        print("FAILED smart formatting type")
        return False

    print("Smart formatting test passed")

    return True


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 50)
    print("AkshAI Formatter Engine v1.0")
    print("=" * 50)

    if run_formatter_test():

        print(
            "\nFORMATTER ENGINE TEST PASSED ✅"
        )

    else:

        print(
            "\nFORMATTER ENGINE TEST FAILED ❌"
        )