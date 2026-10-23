"""
AkshAI AI Engine v1.0
=====================

Purpose:
    AI/LLM layer for AkshAI.

Features:
    - Prompt building
    - Conversation context
    - System instructions
    - Engine-result integration
    - Natural answer generation
    - Optional LLM API support
    - Safe fallback when API is unavailable
    - Structured AIResult

Author:
    Akshay Yadav
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import json
import os
import re
import time
import urllib.request
import urllib.error


# ============================================================
# CONSTANTS
# ============================================================

ENGINE_NAME = "AkshAI AI Engine"
ENGINE_VERSION = "1.2"

DEFAULT_PROVIDER = os.environ.get(
    "AI_PROVIDER", "gemini"
).strip().lower()

DEFAULT_MODEL = os.environ.get(
    "AI_MODEL",
    "gemini-3.1-flash-lite"
    if DEFAULT_PROVIDER == "gemini"
    else "gpt-5.6-luna",
)

OPENAI_API_URL = "https://api.openai.com/v1/responses"

GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "openai/chat/completions"
)

DEFAULT_TIMEOUT = 60


SYSTEM_PROMPT = """
You are AkshAI, a helpful, intelligent and friendly AI assistant.

Your goals:
- Understand the user's actual intent.
- Give accurate and useful answers.
- Never invent facts when information is uncertain.
- Use available tool/engine results when provided.
- Respect the conversation context.
- Keep answers natural and easy to understand.
- Use bullets and numbering when useful.
- Use appropriate emojis naturally, not excessively.
- Match the user's language: Hindi, English or Hinglish.
- For academic questions, explain clearly with examples when useful.
- For coding questions, provide complete and runnable code when requested.
- For writing requests, produce natural, polished text.
- For current information, rely on fresh web/tool information when available.
"""


# ============================================================
# RESULT MODEL
# ============================================================

@dataclass
class AIResult:
    """
    Standard result returned by AI Engine.
    """

    success: bool = False

    query: str = ""
    answer: str = ""

    model: str = ""
    language: str = ""

    source: str = "ai"

    prompt: str = ""

    context_used: bool = False
    engine_results_used: bool = False

    error: str = ""
    error_type: str = ""

    data: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "query": self.query,
            "answer": self.answer,
            "model": self.model,
            "language": self.language,
            "source": self.source,
            "prompt": self.prompt,
            "context_used": self.context_used,
            "engine_results_used": (
                self.engine_results_used
            ),
            "error": self.error,
            "error_type": self.error_type,
            "data": self.data,
        }


# ============================================================
# AI ENGINE
# ============================================================
class AIEngine:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        self.provider = DEFAULT_PROVIDER

        if self.provider == "gemini":
            self.api_key = (
                api_key
                or os.environ.get("GEMINI_API_KEY", "")
                or os.environ.get("GOOGLE_API_KEY", "")
            )
        else:
            self.api_key = (
                api_key
                or os.environ.get("OPENAI_API_KEY", "")
            )

        self.model = model
        self.timeout = max(
            5,
            int(timeout),
        )

    # ========================================================
    # TEXT CLEANING
    # ========================================================

    def clean_text(self, text: Any) -> str:
        """
        Clean and normalize text.
        """

        if text is None:
            return ""

        text = str(text)

        # Remove trailing/leading spaces from every line
        lines = [
            line.strip()
            for line in text.splitlines()
        ]

        text = "\n".join(lines)

        # Normalize multiple spaces/tabs
        text = re.sub(r"[ \t]+", " ", text)

        # Keep maximum two consecutive newlines
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

        # ========================================================
    # LANGUAGE DETECTION
    # ========================================================

    def detect_language(
        self,
        text: Any,
    ) -> str:

        if not isinstance(text, str):
            return "unknown"

        text = text.strip()

        if not text:
            return "unknown"

        hindi_chars = len(
            re.findall(
                r"[\u0900-\u097F]",
                text,
            )
        )

        english_chars = len(
            re.findall(
                r"[A-Za-z]",
                text,
            )
        )

        if hindi_chars > 0 and english_chars > 0:
            return "hinglish"

        if hindi_chars > 0:
            return "hindi"

        if english_chars == 0:
            return "unknown"

        roman_hindi_words = {
            "main", "mein", "mera", "meri", "mere",
            "mujhe", "mujhse", "hum", "ham",
            "aap", "aapka", "aapki", "aapke",
            "tum", "tumhara", "tumhari", "tumhare",
            "hai", "hain", "ho", "tha", "thi", "the",
            "kya", "kyu", "kyon", "kaise",
            "ka", "ke", "ki", "ko",
            "se", "me", "par", "pe",
            "ye", "yeh", "woh", "vo",
            "is", "us", "iska", "uska",
            "kar", "karo", "kr", "krna",
            "bata", "batao", "bta",
            "chahiye", "chahta", "chahti",
            "acha", "accha", "achha",
            "bahut", "bohot",
            "nahi", "nahin", "nhi",
            "abhi", "aaj", "kal",
            "yahan", "wahan",
            "sab", "kuch", "koi",
            "kaam", "padhai", "padho",
            "ghar", "dost", "bhai", "yaar",
            "kyunki", "lekin", "aur",
            "toh", "to", "bhi",
        }

        words = re.findall(
            r"[A-Za-z]+",
            text.lower(),
        )

        roman_hindi_count = sum(
            1
            for word in words
            if word in roman_hindi_words
        )

        if roman_hindi_count >= 1:
            return "hinglish"

        return "english"

    # ========================================================
    # LANGUAGE INSTRUCTION
    # ========================================================

    def language_instruction(
        self,
        language: str,
    ) -> str:

        mapping = {
            "hindi": (
                "Respond primarily in natural Hindi."
            ),
            "english": (
                "Respond in clear natural English."
            ),
            "hinglish": (
                "Respond in natural Hinglish, "
                "mixing Hindi and English comfortably."
            ),
            "unknown": (
                "Respond in the language that "
                "best matches the user's message."
            ),
        }

        return mapping.get(
            language,
            mapping["unknown"],
        )

    # ========================================================
    # SYSTEM PROMPT
    # ========================================================

    def get_system_prompt(
        self,
        language: str = "unknown",
    ) -> str:

        return (
            SYSTEM_PROMPT.strip()
            + "\n\n"
            + self.language_instruction(
                language
            )
        )

    # ========================================================
    # CONTEXT NORMALIZATION
    # ========================================================

    def normalize_context(
        self,
        context: Any,
    ) -> str:

        if context is None:
            return ""

        if isinstance(
            context,
            str,
        ):
            return self.clean_text(
                context
            )

        if isinstance(
            context,
            list,
        ):

            lines = []

            for item in context:

                if isinstance(
                    item,
                    dict,
                ):
                    role = item.get(
                        "role",
                        "",
                    )

                    content = item.get(
                        "content",
                        "",
                    )

                    if content:
                        lines.append(
                            f"{role}: {content}"
                        )

                else:
                    lines.append(
                        str(item)
                    )

            return self.clean_text(
                "\n".join(lines)
            )

        if isinstance(
            context,
            dict,
        ):

            return self.clean_text(
                json.dumps(
                    context,
                    ensure_ascii=False,
                )
            )

        return self.clean_text(
            str(context)
        )

    # ========================================================
    # ENGINE RESULTS
    # ========================================================

    def normalize_engine_results(
        self,
        results: Any,
    ) -> str:

        if results is None:
            return ""

        if isinstance(
            results,
            str,
        ):
            return self.clean_text(
                results
            )

        if isinstance(
            results,
            list,
        ):

            parts = []

            for index, item in enumerate(
                results,
                start=1,
            ):

                if isinstance(
                    item,
                    dict,
                ):
                    parts.append(
                        f"Engine Result {index}:\n"
                        + json.dumps(
                            item,
                            ensure_ascii=False,
                            indent=2,
                        )
                    )

                else:
                    parts.append(
                        f"Engine Result {index}:\n"
                        f"{item}"
                    )

            return self.clean_text(
                "\n\n".join(parts)
            )

        if isinstance(
            results,
            dict,
        ):

            return self.clean_text(
                json.dumps(
                    results,
                    ensure_ascii=False,
                    indent=2,
                )
            )

        return self.clean_text(
            str(results)
        )

    # ========================================================
    # PROMPT BUILDER
    # ========================================================

    def build_prompt(
        self,
        query: str,
        context: Any = None,
        engine_results: Any = None,
        language: Optional[str] = None,
    ) -> str:

        query = self.clean_text(
            query
        )

        detected_language = (
            language
            or self.detect_language(
                query
            )
        )

        sections = []

        sections.append(
            "USER QUESTION:\n"
            + query
        )

        context_text = (
            self.normalize_context(
                context
            )
        )

        if context_text:
            sections.append(
                "CONVERSATION CONTEXT:\n"
                + context_text
            )

        engine_text = (
            self.normalize_engine_results(
                engine_results
            )
        )

        if engine_text:
            sections.append(
                "AVAILABLE ENGINE INFORMATION:\n"
                + engine_text
            )

        sections.append(
            "RESPONSE LANGUAGE:\n"
            + detected_language
        )

        sections.append(
            "INSTRUCTION:\n"
            "Generate the best possible answer "
            "using the available information."
        )

        return "\n\n".join(
            sections
        )

    # ========================================================
    # API REQUEST BODY
    # ========================================================

    
    def build_api_payload(
        self,
        query: str,
        context: Any = None,
        engine_results: Any = None,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:

        detected_language = (
            language or self.detect_language(query)
        )

        prompt = self.build_prompt(
            query=query,
            context=context,
            engine_results=engine_results,
            language=detected_language,
        )

        system_prompt = self.get_system_prompt(
            detected_language
        )

        if self.provider == "gemini":
            return {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
            }

        return {
            "model": self.model,
            "instructions": system_prompt,
            "input": prompt,
        }


    # ========================================================
    # API REQUEST
    # ========================================================

    def request_api(
        self,
        payload: Dict[str, Any],
        _retry_attempt: int = 0,
    ) -> AIResult:

        if not self.api_key:
            return AIResult(
                success=False,
                source="ai",
                model=self.model,
                error=(
                    f"{self.provider.upper()} API key is not configured."
                ),
                error_type="missing_api_key",
            )

        body = json.dumps(
            payload,
            ensure_ascii=False,
        ).encode("utf-8")

        request = urllib.request.Request(
                        (
                GEMINI_API_URL
                if self.provider == "gemini"
                else OPENAI_API_URL
            ),
            data=body,
            method="POST",
            headers={
                "Authorization": (
                    "Bearer "
                    + self.api_key
                ),
                "Content-Type": (
                    "application/json"
                ),
            },
        )

        try:

            with urllib.request.urlopen(
                request,
                timeout=self.timeout,
            ) as response:

                raw = response.read()

                text = raw.decode(
                    "utf-8",
                    errors="replace",
                )

                data = json.loads(
                    text
                )

                answer = self.extract_answer(data)

                if not answer:

                    return AIResult(
                        success=False,
                        model=self.model,
                        source="ai",
                        error=(
                            "AI returned an empty response."
                        ),
                        error_type="empty_response",
                        data=data,
                    )

                return AIResult(
                    success=True,
                    answer=self.clean_text(
                        answer
                    ),
                    model=self.model,
                    source="ai",
                    data={
                        "raw_response": data
                    },
                )

        except urllib.error.HTTPError as exc:

            if (
                exc.code == 503
                and self.provider == "gemini"
                and _retry_attempt < 2
            ):
                exc.close()
                time.sleep(2 * (_retry_attempt + 1))
                return self.request_api(
                    payload,
                    _retry_attempt=_retry_attempt + 1,
                )

            try:
                error_body = (
                    exc.read()
                    .decode(
                        "utf-8",
                        errors="replace",
                    )
                )
            except Exception:
                error_body = ""

            # Try to classify common API failures so the
            # higher-level Brain can choose a fallback.
            error_lower = error_body.lower()

            if exc.code == 401:
                error_type = "authentication_error"
            elif exc.code == 429:
                if (
                    "quota" in error_lower
                    or "credit" in error_lower
                    or "billing" in error_lower
                    or "insufficient_quota" in error_lower
                ):
                    error_type = "insufficient_quota"
                else:
                    error_type = "rate_limit"
            elif exc.code == 403:
                error_type = "permission_error"
            elif exc.code >= 500:
                error_type = "server_error"
            else:
                error_type = "api_http_error"

            return AIResult(
                success=False,
                model=self.model,
                source="ai",
                error=(
                    f"AI API HTTP error "
                    f"{exc.code}: "
                    f"{error_body or exc.reason}"
                ),
                error_type=error_type,
                data={
                    "http_status": exc.code,
                },
            )

        except urllib.error.URLError as exc:

            return AIResult(
                success=False,
                model=self.model,
                source="ai",
                error=(
                    f"AI API connection error: "
                    f"{exc.reason}"
                ),
                error_type="connection_error",
            )

        except TimeoutError:

            return AIResult(
                success=False,
                model=self.model,
                source="ai",
                error="AI API request timed out.",
                error_type="timeout",
            )

        except json.JSONDecodeError:

            return AIResult(
                success=False,
                model=self.model,
                source="ai",
                error=(
                    "AI API returned invalid JSON."
                ),
                error_type="invalid_json",
            )

        except Exception as exc:

            return AIResult(
                success=False,
                model=self.model,
                source="ai",
                error=(
                    f"AI request failed: {exc}"
                ),
                error_type="request_error",
            )
            # ============================================================
# RESPONSE EXTRACTION
# ============================================================

    def extract_answer(
        self,
        data: Any,
    ) -> str:
        """
        Extract answer text from different AI response formats.
        """

        if data is None:
            return ""

        if isinstance(data, str):
            return self.clean_text(data)

        if not isinstance(data, dict):
            return ""

        # Direct output_text.
        output_text = data.get(
            "output_text",
            "",
        )

        if output_text:
            return self.clean_text(
                output_text
            )

        # Responses API output.
        output = data.get(
            "output",
            [],
        )

        if isinstance(output, list):

            parts = []

            for item in output:

                if not isinstance(
                    item,
                    dict,
                ):
                    continue

                content = item.get(
                    "content",
                    [],
                )

                if not isinstance(
                    content,
                    list,
                ):
                    continue

                for block in content:

                    if not isinstance(
                        block,
                        dict,
                    ):
                        continue

                    if block.get(
                        "type"
                    ) == "output_text":

                        text = block.get(
                            "text",
                            "",
                        )

                        if text:
                            parts.append(
                                text
                            )

            if parts:
                return self.clean_text(
                    "\n".join(parts)
                )
        # Gemini / OpenAI-compatible Chat Completions.
        choices = data.get("choices", [])

        if isinstance(choices, list) and choices:
            first_choice = choices[0]

            if isinstance(first_choice, dict):
                message = first_choice.get("message", {})

                if isinstance(message, dict):
                    content = message.get("content", "")

                    if isinstance(content, str) and content.strip():
                        return self.clean_text(content)

                    if isinstance(content, list):
                        parts = [
                            item.get("text", "")
                            for item in content
                            if isinstance(item, dict)
                            and isinstance(item.get("text"), str)
                        ]

                        if parts:
                            return self.clean_text("\n".join(parts))
        # Generic answer fields.
        for key in (
            "answer",
            "response",
            "text",
            "message",
        ):

            value = data.get(
                key,
                "",
            )

            if isinstance(
                value,
                str,
            ) and value.strip():

                return self.clean_text(
                    value
                )

        return ""


# ============================================================
# FALLBACK ANSWER
# ============================================================

    def fallback_answer(
        self,
        query: str,
        context: Any = None,
        engine_results: Any = None,
    ) -> AIResult:
        """
        Safe fallback when external AI is unavailable.

        This does NOT pretend to be an LLM.
        It simply returns available information
        so higher-level engines can continue processing.
        """

        query = self.clean_text(
            query
        )

        language = self.detect_language(
            query
        )

        engine_text = (
            self.normalize_engine_results(
                engine_results
            )
        )

        if engine_text:

            answer = (
                "🤖 AkshAI has gathered the "
                "following information:\n\n"
                + engine_text
            )

        else:

            answer = (
                "🤖 AkshAI is online, but its "
                "external AI model is currently "
                "unavailable. I don't want to "
                "invent an answer without a reliable "
                "source.\n\n"
                "You can still use AkshAI's local "
                "engines, and the AI provider can be "
                "restored later without changing the "
                "app."
            )

        return AIResult(
            success=True,
            query=query,
            answer=self.clean_text(
                answer
            ),
            model="fallback",
            language=language,
            source="ai_fallback",
            context_used=bool(
                context
            ),
            engine_results_used=bool(
                engine_results
            ),
            data={
                "fallback": True,
            },
        )


# ============================================================
# GENERATE
# ============================================================

    def generate(
        self,
        query: Any,
        context: Any = None,
        engine_results: Any = None,
        language: Optional[str] = None,
    ) -> AIResult:
        """
        Generate an AI response.

        If an API key is available:
            Uses the configured LLM API.

        If no API key is available, or the API
        fails (quota, authentication, network,
        timeout, server, etc.):
            Uses a safe fallback result.
        """

        if not isinstance(
            query,
            str,
        ):

            return AIResult(
                success=False,
                source="ai",
                error="Query must be text.",
                error_type="invalid_query",
            )

        query = self.clean_text(
            query
        )

        if not query:

            return AIResult(
                success=False,
                query="",
                source="ai",
                error="Query is empty.",
                error_type="empty_query",
            )

        detected_language = (
            language
            or self.detect_language(
                query
            )
        )

        prompt = self.build_prompt(
            query=query,
            context=context,
            engine_results=engine_results,
            language=detected_language,
        )

        payload = self.build_api_payload(
            query=query,
            context=context,
            engine_results=engine_results,
            language=detected_language,
        )

        # ----------------------------------------------------
        # No API key → safe fallback
        # ----------------------------------------------------

        if not self.api_key:

            result = self.fallback_answer(
                query=query,
                context=context,
                engine_results=engine_results,
            )

            result.prompt = prompt

            return result

        # ----------------------------------------------------
        # API request
        # ----------------------------------------------------

        result = self.request_api(
            payload
        )

        result.query = query
        result.language = detected_language
        result.prompt = prompt
        result.context_used = bool(
            context
        )
        result.engine_results_used = bool(
            engine_results
        )

        # ----------------------------------------------------
        # API failed → use the safe fallback instead of
        # making AkshAI unusable. The original error is
        # preserved in the fallback result for diagnostics.
        # ----------------------------------------------------

        if not result.success:

            fallback = self.fallback_answer(
                query=query,
                context=context,
                engine_results=engine_results,
            )

            fallback.prompt = prompt
            fallback.query = query
            fallback.language = detected_language
            fallback.context_used = bool(
                context
            )
            fallback.engine_results_used = bool(
                engine_results
            )

            fallback.data.update({
                "ai_failed": True,
                "ai_error_type": result.error_type,
                "ai_error": result.error,
                "ai_model": result.model,
            })

            return fallback

        return result


# ============================================================
# ANSWER
# ============================================================

    def answer(
        self,
        query: Any,
        context: Any = None,
        engine_results: Any = None,
        language: Optional[str] = None,
    ) -> str:
        """
        Simple interface returning answer text.
        """

        result = self.generate(
            query=query,
            context=context,
            engine_results=engine_results,
            language=language,
        )

        if result.success:
            return result.answer

        return (
            "❌ "
            + (
                result.error
                or "Unable to generate an answer."
            )
        )


# ============================================================
# PREPARE ENGINE INFORMATION
# ============================================================

    def prepare_engine_information(
        self,
        **engines: Any,
    ) -> Dict[str, Any]:
        """
        Prepare multiple engine outputs for AI.
        """

        prepared = {}

        for name, result in engines.items():

            if result is None:
                continue

            if isinstance(
                result,
                dict,
            ):

                prepared[name] = result

            elif hasattr(
                result,
                "to_dict",
            ):

                try:
                    prepared[name] = (
                        result.to_dict()
                    )

                except Exception:
                    prepared[name] = str(
                        result
                    )

            else:
                prepared[name] = str(
                    result
                )

        return prepared


# ============================================================
# STATUS
# ============================================================

    def status(self) -> Dict[str, Any]:
        """
        Return AI Engine status.
        """

        return {
            "engine": ENGINE_NAME,
            "version": ENGINE_VERSION,
            "status": "ready",
            "model": self.model,
            "api_configured": bool(
                self.api_key
            ),
            "features": [
                "language_detection",
                "system_prompt",
                "context_handling",
                "engine_result_integration",
                "prompt_building",
                "llm_generation",
                "safe_fallback",
                "api_error_classification",
                "api_failure_fallback",
                "response_extraction",
            ],
        }


# ============================================================
# GLOBAL ENGINE
# ============================================================

_ai_engine = AIEngine()


# ============================================================
# PUBLIC FUNCTIONS
# ============================================================

def generate_ai_response(
    query: str,
    context: Any = None,
    engine_results: Any = None,
    language: Optional[str] = None,
) -> AIResult:
    """
    Generate an AI response.
    """

    return _ai_engine.generate(
        query=query,
        context=context,
        engine_results=engine_results,
        language=language,
    )


def ask_ai(
    query: str,
    context: Any = None,
    engine_results: Any = None,
    language: Optional[str] = None,
) -> str:
    """
    Simple AI question interface.
    """

    return _ai_engine.answer(
        query=query,
        context=context,
        engine_results=engine_results,
        language=language,
    )


def get_ai_status() -> Dict[str, Any]:
    """
    Return AI Engine status.
    """

    return _ai_engine.status()


# ============================================================
# SELF TEST
# ============================================================

def run_self_test() -> bool:
    """
    Run AI Engine self-tests.
    """

    # Force an environment-independent self-test.
    # The normal AIEngine still reads OPENAI_API_KEY from the environment.
    engine = AIEngine(
        api_key="__SELF_TEST_NO_KEY__"
    )
    engine.api_key = ""

    passed = 0
    total = 0

    def test(
        name: str,
        condition: bool,
    ) -> None:

        nonlocal passed, total

        total += 1

        if condition:
            passed += 1
            print(
                f"{name} test passed"
            )
        else:
            print(
                f"{name} test FAILED"
            )

    print(
        f"{ENGINE_NAME} v{ENGINE_VERSION}"
    )
    print("=" * 55)

    # --------------------------------------------------------
    # 1. Text cleaning
    # --------------------------------------------------------

    cleaned = engine.clean_text(
        "Hello AkshAI\n\nWorld",
    )

    test(
        "Text cleaning",
        cleaned == "Hello AkshAI\n\nWorld",
    )

    # --------------------------------------------------------
    # 2. English detection
    # --------------------------------------------------------

    test(
        "English detection",
        engine.detect_language(
            "Hello, how are you?"
        )
        == "english",
    )

    # --------------------------------------------------------
    # 3. Hindi detection
    # --------------------------------------------------------

    test(
        "Hindi detection",
        engine.detect_language(
            "आप कैसे हैं?"
        )
        == "hindi",
    )

    # --------------------------------------------------------
    # 4. Hinglish detection
    # --------------------------------------------------------

    test(
        "Hinglish detection",
        engine.detect_language(
            "Bhai aaj weather kaisa hai?"
        )
        == "hinglish",
    )

    # --------------------------------------------------------
    # 5. Empty language
    # --------------------------------------------------------

    test(
        "Empty language handling",
        engine.detect_language("")
        == "unknown",
    )

    # --------------------------------------------------------
    # 6. Language instruction
    # --------------------------------------------------------

    test(
        "Language instruction",
        "Hinglish"
        in engine.language_instruction(
            "hinglish"
        ),
    )

    # --------------------------------------------------------
    # 7. System prompt
    # --------------------------------------------------------

    system_prompt = (
        engine.get_system_prompt(
            "english"
        )
    )

    test(
        "System prompt",
        (
            "AkshAI"
            in system_prompt
            and "English"
            in system_prompt
        ),
    )

    # --------------------------------------------------------
    # 8. Context normalization
    # --------------------------------------------------------

    context = engine.normalize_context(
        [
            {
                "role": "user",
                "content": "Hello AkshAI",
            },
            {
                "role": "assistant",
                "content": "Hello!",
            },
        ]
    )

    test(
        "Context normalization",
        (
            "user: Hello AkshAI"
            in context
            and "assistant: Hello!"
            in context
        ),
    )

    # --------------------------------------------------------
    # 9. Engine result normalization
    # --------------------------------------------------------

    engine_info = (
        engine.normalize_engine_results(
            {
                "weather": {
                    "temperature": 30
                }
            }
        )
    )

    test(
        "Engine result normalization",
        "temperature" in engine_info,
    )

    # --------------------------------------------------------
    # 10. Prompt building
    # --------------------------------------------------------

    prompt = engine.build_prompt(
        query="Explain gravity",
        context="We are studying physics.",
        engine_results={
            "knowledge": "Gravity attracts masses."
        },
        language="english",
    )

    test(
        "Prompt building",
        (
            "Explain gravity"
            in prompt
            and "physics"
            in prompt
            and "Gravity"
            in prompt
        ),
    )

    # --------------------------------------------------------
    # 11. API payload
    # --------------------------------------------------------

    payload = engine.build_api_payload(
        query="Hello",
        language="english",
    )

    test(
        "API payload",
        (
            payload["model"]
            == engine.model
            and "instructions"
            in payload
            and "input"
            in payload
        ),
    )

    # --------------------------------------------------------
    # 12. Missing API key
    # --------------------------------------------------------

    api_result = engine.request_api(
        payload
    )

    test(
        "Missing API key handling",
        (
            not api_result.success
            and api_result.error_type
            == "missing_api_key"
        ),
    )

    # --------------------------------------------------------
    # 13. Answer extraction
    # --------------------------------------------------------

    extracted = engine.extract_answer(
        {
            "output_text": "Hello AkshAI"
        }
    )

    test(
        "Answer extraction",
        extracted == "Hello AkshAI",
    )

    # --------------------------------------------------------
    # 14. Nested answer extraction
    # --------------------------------------------------------

    nested = engine.extract_answer(
        {
            "output": [
                {
                    "content": [
                        {
                            "type": "output_text",
                            "text": "Nested answer",
                        }
                    ]
                }
            ]
        }
    )

    test(
        "Nested answer extraction",
        nested == "Nested answer",
    )

    # --------------------------------------------------------
    # 15. Empty query
    # --------------------------------------------------------

    empty = engine.generate(
        ""
    )

    test(
        "Empty query handling",
        (
            not empty.success
            and empty.error_type
            == "empty_query"
        ),
    )

    # --------------------------------------------------------
    # 16. Invalid query
    # --------------------------------------------------------

    invalid = engine.generate(
        None
    )

    test(
        "Invalid query handling",
        (
            not invalid.success
            and invalid.error_type
            == "invalid_query"
        ),
    )

    # --------------------------------------------------------
    # 17. Fallback generation
    # --------------------------------------------------------

    fallback = engine.generate(
        "Explain gravity",
        engine_results={
            "knowledge": (
                "Gravity is an attractive force."
            )
        },
    )

    test(
        "Fallback generation",
        (
            fallback.success
            and fallback.source
            == "ai_fallback"
            and "Gravity"
            in fallback.answer
        ),
    )

    # --------------------------------------------------------
    # 18. Context flag
    # --------------------------------------------------------

    context_result = engine.generate(
        "Continue",
        context="Previous conversation",
    )

    test(
        "Context flag",
        context_result.context_used,
    )

    # --------------------------------------------------------
    # 19. Engine result flag
    # --------------------------------------------------------

    result_flag = engine.generate(
        "Explain this",
        engine_results={
            "knowledge": "Test information"
        },
    )

    test(
        "Engine result flag",
        result_flag.engine_results_used,
    )

    # --------------------------------------------------------
    # 20. Engine information preparation
    # --------------------------------------------------------

    prepared = (
        engine.prepare_engine_information(
            knowledge={
                "answer": "Test",
            },
            weather="Sunny",
            empty=None,
        )
    )

    test(
        "Engine information preparation",
        (
            "knowledge" in prepared
            and "weather" in prepared
            and "empty" not in prepared
        ),
    )

    # --------------------------------------------------------
    # 21. Status
    # --------------------------------------------------------

    status = engine.status()

    test(
        "Status",
        (
            status["engine"]
            == ENGINE_NAME
            and status["version"]
            == ENGINE_VERSION
            and status["status"]
            == "ready"
            and status["api_configured"]
            is False
        ),
    )

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    print("-" * 55)

    print(
        f"Tests passed: {passed}/{total}"
    )

    if passed == total:
        print(
            "AI ENGINE TEST PASSED ✅"
        )
        return True

    print(
        "AI ENGINE TEST FAILED ❌"
    )

    return False


# ============================================================
# MODULE ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_self_test()