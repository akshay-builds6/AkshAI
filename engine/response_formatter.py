# ========================================================
# AKSHAI RESPONSE FORMATTER v1.0
# Presentation • Styling • Structured Output
# ========================================================

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


# ========================================================
# ENGINE CONFIG
# ========================================================

ENGINE_NAME = "AkshAI Response Formatter"
ENGINE_VERSION = "1.0"


# ========================================================
# FORMAT RESULT
# ========================================================

@dataclass
class FormatResult:
    success: bool
    original: str = ""
    formatted: str = ""
    response_type: str = "general"
    language: str = ""
    error: str = ""
    error_type: str = ""


# ========================================================
# RESPONSE FORMATTER
# ========================================================

class ResponseFormatter:

    def __init__(self):
        self.engine_name = ENGINE_NAME
        self.version = ENGINE_VERSION

    # ====================================================
    # CLEAN TEXT
    # ====================================================

    def clean_text(self, text: Any) -> str:
        if text is None:
            return ""

        text = str(text)

        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        lines = []

        for line in text.split("\n"):
            line = line.strip()
            lines.append(line)

        result = "\n".join(lines).strip()

        while "\n\n\n" in result:
            result = result.replace("\n\n\n", "\n\n")

        return result

    # ====================================================
    # REMOVE EXCESSIVE SPACES
    # ====================================================

    def normalize_spaces(self, text: str) -> str:

        text = self.clean_text(text)

        lines = []

        for line in text.split("\n"):

            if line.strip():
                lines.append(
                    " ".join(line.split())
                )
            else:
                lines.append("")

        return "\n".join(lines).strip()

    # ====================================================
    # DETECT RESPONSE TYPE
    # ====================================================

    def detect_response_type(
        self,
        response_type: str = "",
        source: str = ""
    ) -> str:

        response_type = self.clean_text(
            response_type
        ).lower()

        source = self.clean_text(
            source
        ).lower()

        if response_type:
            return response_type

        if "calculator" in source:
            return "calculation"

        if "weather" in source:
            return "weather"

        if "search" in source:
            return "search"

        if "knowledge" in source:
            return "knowledge"

        if "memory" in source:
            return "memory"

        if "notes" in source:
            return "notes"

        if "profile" in source:
            return "profile"

        if "coding" in source:
            return "coding"

        return "general"

    # ====================================================
    # EMOJI MAPPING
    # ====================================================

    def get_emoji(
        self,
        response_type: str
    ) -> str:

        mapping = {

            "calculation": "🧮",
            "math": "📐",
            "physics": "⚡",
            "chemistry": "⚛️",
            "biology": "🧬",
            "coding": "💻",
            "weather": "🌦️",
            "search": "🔎",
            "knowledge": "🧠",
            "memory": "💾",
            "notes": "📝",
            "profile": "👤",
            "writing": "✍️",
            "explanation": "📚",
            "conversation": "💬",
            "general": "✨",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",

        }

        return mapping.get(
            response_type,
            "✨"
        )

    # ====================================================
    # HEADING
    # ====================================================

    def format_heading(
        self,
        title: str,
        emoji: Optional[str] = None
    ) -> str:

        title = self.clean_text(
            title
        )

        if not title:
            return ""

        if emoji is None:
            emoji = "✨"

        return (
            f"{emoji} **{title}**"
        )

    # ====================================================
    # BULLET LIST
    # ====================================================

    def format_bullets(
        self,
        items: List[Any]
    ) -> str:

        if not items:
            return ""

        lines = []

        for item in items:

            item = self.clean_text(
                item
            )

            if item:
                lines.append(
                    f"• {item}"
                )

        return "\n".join(lines)

    # ====================================================
    # NUMBERED LIST
    # ====================================================

    def format_numbered(
        self,
        items: List[Any]
    ) -> str:

        if not items:
            return ""

        lines = []

        number = 1

        for item in items:

            item = self.clean_text(
                item
            )

            if item:

                lines.append(
                    f"{number}. {item}"
                )

                number += 1

        return "\n".join(lines)

    # ====================================================
    # TABLE
    # ====================================================

    def format_table(
        self,
        headers: List[Any],
        rows: List[List[Any]]
    ) -> str:

        if not headers:
            return ""

        headers = [
            self.clean_text(header)
            for header in headers
        ]

        rows = [
            [
                self.clean_text(cell)
                for cell in row
            ]
            for row in rows
        ]

        header_line = (
            "| "
            + " | ".join(headers)
            + " |"
        )

        separator = (
            "| "
            + " | ".join(
                "---"
                for _ in headers
            )
            + " |"
        )

        lines = [
            header_line,
            separator
        ]

        for row in rows:

            if len(row) < len(headers):

                row = row + [
                    ""
                ] * (
                    len(headers) - len(row)
                )

            elif len(row) > len(headers):

                row = row[
                    :len(headers)
                ]

            lines.append(
                "| "
                + " | ".join(row)
                + " |"
            )

        return "\n".join(lines)

    # ====================================================
    # CODE BLOCK
    # ====================================================

    def format_code(
        self,
        code: str,
        language: str = ""
    ) -> str:

        code = str(code)

        language = self.clean_text(
            language
        ).lower()

        return (
            f"```{language}\n"
            f"{code.rstrip()}\n"
            "```"
        )

    # ====================================================
    # CALCULATOR
    # ====================================================

    def format_calculation(
        self,
        result: Any
    ) -> str:

        result = self.clean_text(
            result
        )

        if not result:
            return (
                "🧮 **Calculation Result**\n\n"
                "No result available."
            )

        return (
            "🧮 **Calculation Result**\n\n"
            f"✅ **Answer:** {result}"
        )

    # ====================================================
    # WEATHER
    # ====================================================

    def format_weather(
        self,
        data: Dict[str, Any]
    ) -> str:

        if not isinstance(
            data,
            dict
        ):

            return self.clean_text(
                data
            )

        lines = [
            "🌦️ **Weather Update**"
        ]

        location = data.get(
            "location",
            ""
        )

        if location:

            lines.append(
                f"📍 **Location:** {location}"
            )

        temperature = data.get(
            "temperature",
            data.get("temp", "")
        )

        if temperature != "":
            lines.append(
                f"🌡️ **Temperature:** {temperature}"
            )

        condition = data.get(
            "condition",
            data.get("description", "")
        )

        if condition:
            lines.append(
                f"☁️ **Condition:** {condition}"
            )

        humidity = data.get(
            "humidity",
            ""
        )

        if humidity != "":
            lines.append(
                f"💧 **Humidity:** {humidity}"
            )

        wind = data.get(
            "wind",
            data.get("wind_speed", "")
        )

        if wind != "":
            lines.append(
                f"💨 **Wind:** {wind}"
            )

        return "\n".join(lines)

    # ====================================================
    # SEARCH RESULTS
    # ====================================================

    def format_search_results(
        self,
        results: List[Any]
    ) -> str:

        if not results:

            return (
                "🔎 **Search Results**\n\n"
                "No results found."
            )

        lines = [
            "🔎 **Search Results**",
            ""
        ]

        number = 1

        for result in results:

            if isinstance(
                result,
                dict
            ):

                title = self.clean_text(
                    result.get(
                        "title",
                        f"Result {number}"
                    )
                )

                description = self.clean_text(
                    result.get(
                        "description",
                        result.get(
                            "snippet",
                            ""
                        )
                    )
                )

                lines.append(
                    f"{number}. **{title}**"
                )

                if description:
                    lines.append(
                        f"   📌 {description}"
                    )

            else:

                text = self.clean_text(
                    result
                )

                if text:

                    lines.append(
                        f"{number}. {text}"
                    )

            number += 1

        return "\n".join(lines)

    # ====================================================
    # ERROR
    # ====================================================

    def format_error(
        self,
        error: str
    ) -> str:

        error = self.clean_text(
            error
        )

        if not error:

            error = (
                "Something went wrong."
            )

        return (
            "❌ **Something went wrong**\n\n"
            f"⚠️ {error}"
        )

    # ====================================================
    # WARNING
    # ====================================================

    def format_warning(
        self,
        message: str
    ) -> str:

        message = self.clean_text(
            message
        )

        return (
            "⚠️ **Warning**\n\n"
            f"{message}"
        )

    # ====================================================
    # SUCCESS
    # ====================================================

    def format_success(
        self,
        message: str
    ) -> str:

        message = self.clean_text(
            message
        )

        return (
            "✅ **Success**\n\n"
            f"{message}"
        )

    # ====================================================
    # GENERAL RESPONSE
    # ====================================================

    def format_general(
        self,
        response: str,
        response_type: str = "general"
    ) -> str:

        response = self.clean_text(
            response
        )

        if not response:
            return ""

        # Already formatted markdown/code
        if (
            response.startswith("```")
            or response.startswith("|")
        ):
            return response

        return response

    # ====================================================
    # AUTO EMOJI
    # ====================================================

    def add_context_emoji(
        self,
        response: str,
        response_type: str
    ) -> str:

        response = self.clean_text(
            response
        )

        if not response:
            return ""

        emoji = self.get_emoji(
            response_type
        )

        markers = (
            "🧮",
            "📐",
            "⚡",
            "⚛️",
            "🧬",
            "💻",
            "🌦️",
            "🔎",
            "🧠",
            "💾",
            "📝",
            "👤",
            "✍️",
            "📚",
            "💬",
            "✨",
            "✅",
            "⚠️",
            "❌",
        )

        if response.startswith(markers):
            return response

        return f"{emoji} {response}"

    # ====================================================
    # SMART FORMAT
    # ====================================================

    def smart_format(
        self,
        response: Any,
        response_type: str = "general",
        source: str = "",
        language: str = ""
    ) -> FormatResult:

        original = self.clean_text(
            response
        )

        if not original:

            return FormatResult(
                success=False,
                original="",
                formatted="",
                response_type=response_type,
                language=language,
                error="Empty response.",
                error_type="empty_response"
            )

        response_type = self.detect_response_type(
            response_type=response_type,
            source=source
        )

        # ------------------------------------------------
        # DICTIONARY DATA
        # ------------------------------------------------

        if isinstance(
            response,
            dict
        ):

            if response_type == "weather":

                formatted = self.format_weather(
                    response
                )

            elif response_type == "calculation":

                value = response.get(
                    "answer",
                    response.get(
                        "result",
                        response.get(
                            "value",
                            ""
                        )
                    )
                )

                formatted = self.format_calculation(
                    value
                )

            else:

                text = response.get(
                    "response",
                    response.get(
                        "answer",
                        response.get(
                            "text",
                            ""
                        )
                    )
                )

                formatted = self.format_general(
                    text,
                    response_type
                )

        # ------------------------------------------------
        # LIST DATA
        # ------------------------------------------------

        elif isinstance(
            response,
            list
        ):

            if response_type == "search":

                formatted = self.format_search_results(
                    response
                )

            else:

                formatted = self.format_bullets(
                    response
                )

        # ------------------------------------------------
        # TEXT DATA
        # ------------------------------------------------

        else:

            formatted = self.format_general(
                original,
                response_type
            )

        # ------------------------------------------------
        # CONTEXT EMOJI
        # ------------------------------------------------

        if formatted:

            formatted = self.add_context_emoji(
                formatted,
                response_type
            )

        return FormatResult(
            success=True,
            original=original,
            formatted=formatted,
            response_type=response_type,
            language=language
        )

    # ====================================================
    # FINAL FORMAT
    # ====================================================

    def format(
        self,
        response: Any,
        response_type: str = "general",
        source: str = "",
        language: str = ""
    ) -> str:

        result = self.smart_format(
            response=response,
            response_type=response_type,
            source=source,
            language=language
        )

        if not result.success:

            return self.format_error(
                result.error
            )

        return result.formatted

    # ====================================================
    # STATUS
    # ====================================================

    def status(self) -> Dict[str, Any]:

        return {

            "engine": self.engine_name,

            "version": self.version,

            "features": [
                "text_cleaning",
                "space_normalization",
                "response_type_detection",
                "emoji_mapping",
                "headings",
                "bullet_lists",
                "numbered_lists",
                "tables",
                "code_blocks",
                "calculator_formatting",
                "weather_formatting",
                "search_formatting",
                "error_formatting",
                "warning_formatting",
                "success_formatting",
                "smart_formatting",
                "mobile_friendly_output",
            ]

        }
        # ========================================================
# GLOBAL ENGINE
# ========================================================

_formatter = ResponseFormatter()


# ========================================================
# PUBLIC FUNCTIONS
# ========================================================

def format_response(
    response: Any,
    response_type: str = "general",
    source: str = "",
    language: str = ""
) -> FormatResult:

    return _formatter.smart_format(
        response=response,
        response_type=response_type,
        source=source,
        language=language
    )


def smart_format(
    response: Any,
    response_type: str = "general",
    source: str = "",
    language: str = ""
) -> str:

    return _formatter.format(
        response=response,
        response_type=response_type,
        source=source,
        language=language
    )


def format_bullets(
    items: List[Any]
) -> str:

    return _formatter.format_bullets(
        items
    )


def format_numbered(
    items: List[Any]
) -> str:

    return _formatter.format_numbered(
        items
    )


def format_table(
    headers: List[Any],
    rows: List[List[Any]]
) -> str:

    return _formatter.format_table(
        headers,
        rows
    )


def format_code(
    code: str,
    language: str = ""
) -> str:

    return _formatter.format_code(
        code,
        language
    )


def formatter_status() -> Dict[str, Any]:

    return _formatter.status()


# ========================================================
# SELF TEST
# ========================================================

def run_self_test() -> bool:

    print(
        "AkshAI Response Formatter v1.0"
    )

    print(
        "=" * 55
    )

    engine = ResponseFormatter()

    passed = 0

    # ----------------------------------------------------
    # 1. Cleaning
    # ----------------------------------------------------

    result = engine.clean_text(
        " Hello AkshAI  \n\n\n World "
    )

    assert result == (
        "Hello AkshAI\n\nWorld"
    )

    print(
        "Text cleaning test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # 2. Space normalization
    # ----------------------------------------------------

    result = engine.normalize_spaces(
        "Hello    AkshAI\n\nThis   is   clean"
    )

    assert result == (
        "Hello AkshAI\n\nThis is clean"
    )

    print(
        "Space normalization test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # 3. Emoji mapping
    # ----------------------------------------------------

    assert (
        engine.get_emoji("coding")
        == "💻"
    )

    assert (
        engine.get_emoji("weather")
        == "🌦️"
    )

    print(
        "Emoji mapping test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # 4. Heading
    # ----------------------------------------------------

    result = engine.format_heading(
        "Important Points",
        "📌"
    )

    assert (
        result
        == "📌 **Important Points**"
    )

    print(
        "Heading test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # 5. Bullets
    # ----------------------------------------------------

    result = engine.format_bullets(
        [
            "First",
            "Second",
            "Third"
        ]
    )

    assert (
        result
        == "• First\n• Second\n• Third"
    )

    print(
        "Bullet list test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # 6. Numbered
    # ----------------------------------------------------

    result = engine.format_numbered(
        [
            "First",
            "Second"
        ]
    )

    assert (
        result
        == "1. First\n2. Second"
    )

    print(
        "Numbered list test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # 7. Table
    # ----------------------------------------------------

    result = engine.format_table(
        ["Name", "Age"],
        [
            ["AkshAI", "1"],
            ["User", "16"]
        ]
    )

    assert "| Name | Age |" in result
    assert "| --- | --- |" in result

    print(
        "Table test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # 8. Code
    # ----------------------------------------------------

    result = engine.format_code(
        "print('Hello')",
        "python"
    )

    assert (
        "```python"
        in result
    )

    print(
        "Code block test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # 9. Calculator
    # ----------------------------------------------------

    result = engine.format_calculation(
        "125"
    )

    assert (
        "125"
        in result
    )

    print(
        "Calculator formatting test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # 10. Weather
    # ----------------------------------------------------

    result = engine.format_weather(
        {
            "location": "Delhi",
            "temperature": "30°C",
            "condition": "Clear",
            "humidity": "50%"
        }
    )

    assert "Delhi" in result
    assert "30°C" in result
    assert "Clear" in result

    print(
        "Weather formatting test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # 11. Search
    # ----------------------------------------------------

    result = engine.format_search_results(
        [
            {
                "title": "JEE",
                "description": "Exam information"
            }
        ]
    )

    assert "JEE" in result
    assert "Exam information" in result

    print(
        "Search formatting test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # 12. Error
    # ----------------------------------------------------

    result = engine.format_error(
        "Test error"
    )

    assert "Test error" in result
    assert "❌" in result

    print(
        "Error formatting test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # 13. Smart formatting
    # ----------------------------------------------------

    result = engine.smart_format(
        "Hello AkshAI",
        response_type="general"
    )

    assert result.success
    assert "Hello AkshAI" in result.formatted

    print(
        "Smart formatting test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # 14. Calculation smart formatting
    # ----------------------------------------------------

    result = engine.smart_format(
        {
            "success": True,
            "answer": "25"
        },
        response_type="calculation"
    )

    assert result.success
    assert "25" in result.formatted
    assert "🧮" in result.formatted

    print(
        "Calculation smart formatting test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # 15. Weather smart formatting
    # ----------------------------------------------------

    result = engine.smart_format(
        {
            "location": "Delhi",
            "temperature": "32°C",
            "condition": "Sunny"
        },
        response_type="weather"
    )

    assert result.success
    assert "Delhi" in result.formatted
    assert "32°C" in result.formatted

    print(
        "Weather smart formatting test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # 16. List smart formatting
    # ----------------------------------------------------

    result = engine.smart_format(
        [
            "Point one",
            "Point two"
        ],
        response_type="general"
    )

    assert result.success
    assert "• Point one" in result.formatted
    assert "• Point two" in result.formatted

    print(
        "List smart formatting test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # 17. Empty response
    # ----------------------------------------------------

    result = engine.smart_format(
        ""
    )

    assert not result.success
    assert result.error_type == "empty_response"

    print(
        "Empty response handling test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # 18. Final format
    # ----------------------------------------------------

    result = engine.format(
        "Hello AkshAI",
        response_type="general"
    )

    assert "Hello AkshAI" in result

    print(
        "Final format test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # 19. Status
    # ----------------------------------------------------

    status = engine.status()

    assert (
        status["engine"]
        == ENGINE_NAME
    )

    assert (
        status["version"]
        == ENGINE_VERSION
    )

    assert len(
        status["features"]
    ) > 0

    print(
        "Status test passed"
    )

    passed += 1

    # ----------------------------------------------------
    # FINAL
    # ----------------------------------------------------

    print(
        "-" * 55
    )

    print(
        f"Tests passed: {passed}/19"
    )

    if passed == 19:

        print(
            "RESPONSE FORMATTER TEST PASSED ✅"
        )

        return True

    print(
        "RESPONSE FORMATTER TEST FAILED ❌"
    )

    return False


# ========================================================
# RUN DIRECTLY
# ========================================================

if __name__ == "__main__":

    run_self_test()