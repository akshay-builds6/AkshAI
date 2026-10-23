# ========================================================
# AKSHAI RESPONSE ENGINE v1.0
# Result Processing • Combining • Response Preparation
# ========================================================

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ========================================================
# ENGINE CONFIG
# ========================================================

ENGINE_NAME = "AkshAI Response Engine"
ENGINE_VERSION = "1.0"


# ========================================================
# RESPONSE RESULT
# ========================================================

@dataclass
class ResponseResult:

    success: bool

    query: str = ""

    response: str = ""

    response_type: str = "general"

    intent: str = ""

    language: str = ""

    emotion: str = ""

    source: str = ""

    data: Any = None

    engine_results: List[Dict[str, Any]] = field(
        default_factory=list
    )

    error: str = ""

    error_type: str = ""


# ========================================================
# TEXT HELPERS
# ========================================================

def clean_text(text: Any) -> str:

    if text is None:
        return ""

    text = str(text)

    text = text.replace(
        "\r\n",
        "\n"
    )

    text = text.replace(
        "\r",
        "\n"
    )

    lines = []

    for line in text.split("\n"):

        line = line.strip()

        lines.append(line)

    return "\n".join(
        lines
    ).strip()


# ========================================================
# RESPONSE ENGINE
# ========================================================

class ResponseEngine:

    def __init__(self):

        self.engine_name = ENGINE_NAME

        self.version = ENGINE_VERSION


    # ====================================================
    # RESULT NORMALIZATION
    # ====================================================

    def normalize_result(
        self,
        result: Any,
        source: str = ""
    ) -> Dict[str, Any]:

        if result is None:

            return {
                "success": False,
                "response": "",
                "source": source,
                "error": "No result received.",
                "error_type": "empty_result"
            }


        # ------------------------------------------------
        # DICTIONARY RESULT
        # ------------------------------------------------

        if isinstance(
            result,
            dict
        ):

            normalized = dict(
                result
            )

            normalized.setdefault(
                "success",
                True
            )

            normalized.setdefault(
                "response",
                normalized.get(
                    "answer",
                    normalized.get(
                        "text",
                        ""
                    )
                )
            )

            normalized.setdefault(
                "source",
                source
            )

            return normalized


        # ------------------------------------------------
        # OBJECT / DATACLASS RESULT
        # ------------------------------------------------

        if hasattr(
            result,
            "__dict__"
        ):

            normalized = dict(
                vars(result)
            )

            normalized.setdefault(
                "success",
                True
            )

            normalized.setdefault(
                "response",
                normalized.get(
                    "answer",
                    normalized.get(
                        "text",
                        ""
                    )
                )
            )

            normalized.setdefault(
                "source",
                source
            )

            return normalized


        # ------------------------------------------------
        # STRING RESULT
        # ------------------------------------------------

        if isinstance(
            result,
            str
        ):

            return {
                "success": True,
                "response": clean_text(
                    result
                ),
                "source": source
            }


        # ------------------------------------------------
        # OTHER RESULT
        # ------------------------------------------------

        return {
            "success": True,
            "response": str(
                result
            ),
            "data": result,
            "source": source
        }


    # ====================================================
    # RESPONSE TYPE
    # ====================================================

    def detect_response_type(
        self,
        intent: str = "",
        source: str = "",
        result: Any = None
    ) -> str:

        intent = clean_text(
            intent
        ).lower()

        source = clean_text(
            source
        ).lower()


        if "calculator" in intent:
            return "calculation"

        if "weather" in intent:
            return "weather"

        if "memory" in intent:
            return "memory"

        if "note" in intent:
            return "notes"

        if "profile" in intent:
            return "profile"

        if "knowledge" in intent:
            return "knowledge"

        if "search" in intent:
            return "search"

        if "calculator" in source:
            return "calculation"

        if "weather" in source:
            return "weather"

        if "memory" in source:
            return "memory"

        if "notes" in source:
            return "notes"

        if "profile" in source:
            return "profile"

        if "knowledge" in source:
            return "knowledge"

        if "search" in source:
            return "search"

        return "general"


    # ====================================================
    # RESPONSE EXTRACTION
    # ====================================================

    def extract_response(
        self,
        result: Any
    ) -> str:

        normalized = self.normalize_result(
            result
        )

        response = normalized.get(
            "response",
            ""
        )

        if not response:

            response = normalized.get(
                "answer",
                ""
            )

        if not response:

            response = normalized.get(
                "text",
                ""
            )

        return clean_text(
            response
        )


    # ====================================================
    # COMBINE RESULTS
    # ====================================================

    def combine_results(
        self,
        results: List[Any]
    ) -> str:

        responses = []

        for result in results:

            response = self.extract_response(
                result
            )

            if response:

                if response not in responses:

                    responses.append(
                        response
                    )

        return "\n\n".join(
            responses
        )


    # ====================================================
    # SUCCESS CHECK
    # ====================================================

    def all_successful(
        self,
        results: List[Any]
    ) -> bool:

        if not results:

            return False

        for result in results:

            normalized = self.normalize_result(
                result
            )

            if not normalized.get(
                "success",
                False
            ):

                return False

        return True


    # ====================================================
    # FIRST SUCCESSFUL RESULT
    # ====================================================

    def first_successful(
        self,
        results: List[Any]
    ) -> Optional[Dict[str, Any]]:

        for result in results:

            normalized = self.normalize_result(
                result
            )

            if normalized.get(
                "success",
                False
            ):

                return normalized

        return None


    # ====================================================
    # ERROR EXTRACTION
    # ====================================================

    def extract_error(
        self,
        result: Any
    ) -> str:

        normalized = self.normalize_result(
            result
        )

        return clean_text(
            normalized.get(
                "error",
                ""
            )
        )


    # ====================================================
    # BUILD RESPONSE
    # ====================================================

    def build_response(
        self,
        query: str,
        result: Any = None,
        intent: str = "",
        language: str = "",
        emotion: str = "",
        source: str = ""
    ) -> ResponseResult:

        query = clean_text(
            query
        )

        if not query:

            return ResponseResult(
                success=False,
                query="",
                error="Empty query.",
                error_type="empty_query"
            )


        normalized = self.normalize_result(
            result,
            source
        )

        response = self.extract_response(
            normalized
        )

        result_source = clean_text(
            normalized.get(
                "source",
                source
            )
        )


        response_type = self.detect_response_type(
            intent=intent,
            source=result_source,
            result=normalized
        )


        if not normalized.get(
            "success",
            False
        ):

            error = self.extract_error(
                normalized
            )

            return ResponseResult(
                success=False,
                query=query,
                response="",
                response_type=response_type,
                intent=intent,
                language=language,
                emotion=emotion,
                source=result_source,
                data=normalized,
                error=error or "Engine failed.",
                error_type=normalized.get(
                    "error_type",
                    "engine_error"
                )
            )


        return ResponseResult(
            success=True,
            query=query,
            response=response,
            response_type=response_type,
            intent=intent,
            language=language,
            emotion=emotion,
            source=result_source,
            data=normalized,
            engine_results=[
                normalized
            ]
        )


    # ====================================================
    # BUILD FROM MULTIPLE ENGINES
    # ====================================================

    def build_from_results(
        self,
        query: str,
        results: List[Any],
        intent: str = "",
        language: str = "",
        emotion: str = ""
    ) -> ResponseResult:

        query = clean_text(
            query
        )

        if not query:

            return ResponseResult(
                success=False,
                query="",
                error="Empty query.",
                error_type="empty_query"
            )


        if not results:

            return ResponseResult(
                success=False,
                query=query,
                error="No engine results received.",
                error_type="no_results"
            )


        normalized_results = []

        for result in results:

            normalized_results.append(
                self.normalize_result(
                    result
                )
            )


        successful_results = [
            result
            for result in normalized_results
            if result.get(
                "success",
                False
            )
        ]


        if not successful_results:

            first_error = ""

            for result in normalized_results:

                error = clean_text(
                    result.get(
                        "error",
                        ""
                    )
                )

                if error:

                    first_error = error

                    break


            return ResponseResult(
                success=False,
                query=query,
                intent=intent,
                language=language,
                emotion=emotion,
                error=(
                    first_error
                    or "All engines failed."
                ),
                error_type="all_engines_failed",
                data=normalized_results,
                engine_results=normalized_results
            )


        combined = self.combine_results(
            successful_results
        )


        first = successful_results[0]

        source = clean_text(
            first.get(
                "source",
                ""
            )
        )


        response_type = self.detect_response_type(
            intent=intent,
            source=source
        )


        return ResponseResult(
            success=True,
            query=query,
            response=combined,
            response_type=response_type,
            intent=intent,
            language=language,
            emotion=emotion,
            source=source,
            data=normalized_results,
            engine_results=normalized_results
        )


    # ====================================================
    # PREPARE FOR AI
    # ====================================================

    def prepare_for_ai(
        self,
        query: str,
        response_result: ResponseResult
    ) -> Dict[str, Any]:

        return {

            "query": clean_text(
                query
            ),

            "response": clean_text(
                response_result.response
            ),

            "response_type": response_result.response_type,

            "intent": response_result.intent,

            "language": response_result.language,

            "emotion": response_result.emotion,

            "source": response_result.source,

            "data": response_result.data,

            "success": response_result.success,

        }


    # ====================================================
    # FINAL RESPONSE TEXT
    # ====================================================

    def final_text(
        self,
        result: ResponseResult
    ) -> str:

        if not result.success:

            if result.error:

                return (
                    "😕 Sorry, I couldn't complete that.\n\n"
                    f"⚠️ {result.error}"
                )

            return (
                "😕 Sorry, I couldn't complete that."
            )


        if result.response:

            return result.response


        return (
            "😊 I've processed your request, "
            "but there is no additional information to display."
        )


    # ====================================================
    # STATUS
    # ====================================================

    def status(self) -> Dict[str, Any]:

        return {

            "engine": self.engine_name,

            "version": self.version,

            "features": [
                "result_normalization",
                "response_extraction",
                "response_type_detection",
                "result_combination",
                "success_handling",
                "error_handling",
                "multi_engine_results",
                "ai_preparation",
                "final_response_text",
            ]

        }


# ========================================================
# GLOBAL ENGINE
# ========================================================

_response_engine = ResponseEngine()


# ========================================================
# PUBLIC FUNCTIONS
# ========================================================

def build_response(
    query: str,
    result: Any = None,
    intent: str = "",
    language: str = "",
    emotion: str = "",
    source: str = ""
) -> ResponseResult:

    return _response_engine.build_response(
        query,
        result,
        intent,
        language,
        emotion,
        source
    )


def build_from_results(
    query: str,
    results: List[Any],
    intent: str = "",
    language: str = "",
    emotion: str = ""
) -> ResponseResult:

    return _response_engine.build_from_results(
        query,
        results,
        intent,
        language,
        emotion
    )


def prepare_for_ai(
    query: str,
    response_result: ResponseResult
) -> Dict[str, Any]:

    return _response_engine.prepare_for_ai(
        query,
        response_result
    )


def final_text(
    result: ResponseResult
) -> str:

    return _response_engine.final_text(
        result
    )


def response_status() -> Dict[str, Any]:

    return _response_engine.status()


# ========================================================
# SELF TEST
# ========================================================

def run_self_test() -> bool:

    print(
        "AkshAI Response Engine v1.0"
    )

    print(
        "=" * 55
    )

    engine = ResponseEngine()

    passed = 0


    # ----------------------------------------------------
    # 1. String normalization
    # ----------------------------------------------------

    result = engine.normalize_result(
        "Hello AkshAI"
    )

    assert result["success"]
    assert result["response"] == "Hello AkshAI"

    print(
        "String normalization test passed"
    )

    passed += 1


    # ----------------------------------------------------
    # 2. Dictionary normalization
    # ----------------------------------------------------

    result = engine.normalize_result(
        {
            "success": True,
            "answer": "Test answer"
        },
        source="test_engine"
    )

    assert result["success"]
    assert result["response"] == "Test answer"

    print(
        "Dictionary normalization test passed"
    )

    passed += 1


    # ----------------------------------------------------
    # 3. Object normalization
    # ----------------------------------------------------

    test_object = ResponseResult(
        success=True,
        response="Object answer"
    )

    result = engine.normalize_result(
        test_object
    )

    assert result["success"]
    assert result["response"] == "Object answer"

    print(
        "Object normalization test passed"
    )

    passed += 1


    # ----------------------------------------------------
    # 4. Response extraction
    # ----------------------------------------------------

    assert (
        engine.extract_response(
            {
                "success": True,
                "answer": "Extracted answer"
            }
        )
        == "Extracted answer"
    )

    print(
        "Response extraction test passed"
    )

    passed += 1


    # ----------------------------------------------------
    # 5. Calculator response type
    # ----------------------------------------------------

    assert (
        engine.detect_response_type(
            intent="calculator"
        )
        == "calculation"
    )

    print(
        "Calculator response type test passed"
    )

    passed += 1


    # ----------------------------------------------------
    # 6. Weather response type
    # ----------------------------------------------------

    assert (
        engine.detect_response_type(
            intent="weather"
        )
        == "weather"
    )

    print(
        "Weather response type test passed"
    )

    passed += 1


    # ----------------------------------------------------
    # 7. Combine results
    # ----------------------------------------------------

    combined = engine.combine_results(
        [
            {
                "success": True,
                "answer": "First answer"
            },
            {
                "success": True,
                "answer": "Second answer"
            }
        ]
    )

    assert "First answer" in combined
    assert "Second answer" in combined

    print(
        "Result combination test passed"
    )

    passed += 1


    # ----------------------------------------------------
    # 8. Duplicate prevention
    # ----------------------------------------------------

    combined = engine.combine_results(
        [
            {
                "success": True,
                "answer": "Same answer"
            },
            {
                "success": True,
                "answer": "Same answer"
            }
        ]
    )

    assert combined.count(
        "Same answer"
    ) == 1

    print(
        "Duplicate prevention test passed"
    )

    passed += 1


    # ----------------------------------------------------
    # 9. Success check
    # ----------------------------------------------------

    assert engine.all_successful(
        [
            {
                "success": True
            },
            {
                "success": True
            }
        ]
    )

    print(
        "Success check test passed"
    )

    passed += 1


    # ----------------------------------------------------
    # 10. Failed result detection
    # ----------------------------------------------------

    assert not engine.all_successful(
        [
            {
                "success": True
            },
            {
                "success": False
            }
        ]
    )

    print(
        "Failure detection test passed"
    )

    passed += 1


    # ----------------------------------------------------
    # 11. First successful result
    # ----------------------------------------------------

    result = engine.first_successful(
        [
            {
                "success": False
            },
            {
                "success": True,
                "answer": "Success"
            }
        ]
    )

    assert result is not None
    assert result["answer"] == "Success"

    print(
        "First successful result test passed"
    )

    passed += 1


    # ----------------------------------------------------
    # 12. Build response
    # ----------------------------------------------------

    result = engine.build_response(
        "Calculate 10 + 5",
        {
            "success": True,
            "answer": "15"
        },
        intent="calculator",
        source="calculator_engine"
    )

    assert result.success
    assert result.response == "15"
    assert result.response_type == "calculation"

    print(
        "Build response test passed"
    )

    passed += 1


    # ----------------------------------------------------
    # 13. Failed response
    # ----------------------------------------------------

    result = engine.build_response(
        "Test",
        {
            "success": False,
            "error": "Test error",
            "error_type": "test_error"
        }
    )

    assert not result.success
    assert result.error == "Test error"

    print(
        "Failed response test passed"
    )

    passed += 1


    # ----------------------------------------------------
    # 14. Multiple engine results
    # ----------------------------------------------------

    result = engine.build_from_results(
        "Test question",
        [
            {
                "success": True,
                "answer": "Answer one",
                "source": "knowledge_engine"
            },
            {
                "success": True,
                "answer": "Answer two",
                "source": "internet_engine"
            }
        ]
    )

    assert result.success
    assert "Answer one" in result.response
    assert "Answer two" in result.response

    print(
        "Multiple engine results test passed"
    )

    passed += 1


    # ----------------------------------------------------
    # 15. All engines failed
    # ----------------------------------------------------

    result = engine.build_from_results(
        "Test question",
        [
            {
                "success": False,
                "error": "Failure one"
            },
            {
                "success": False,
                "error": "Failure two"
            }
        ]
    )

    assert not result.success
    assert result.error_type == "all_engines_failed"

    print(
        "All engines failed test passed"
    )

    passed += 1


    # ----------------------------------------------------
    # 16. AI preparation
    # ----------------------------------------------------

    result = engine.build_response(
        "Hello",
        {
            "success": True,
            "answer": "Hi there!"
        },
        intent="greeting",
        language="english",
        emotion="happy"
    )

    ai_data = engine.prepare_for_ai(
        "Hello",
        result
    )

    assert ai_data["query"] == "Hello"
    assert ai_data["response"] == "Hi there!"
    assert ai_data["intent"] == "greeting"
    assert ai_data["emotion"] == "happy"

    print(
        "AI preparation test passed"
    )

    passed += 1


    # ----------------------------------------------------
    # 17. Final text
    # ----------------------------------------------------

    final = engine.final_text(
        result
    )

    assert final == "Hi there!"

    print(
        "Final text test passed"
    )

    passed += 1


    # ----------------------------------------------------
    # 18. Error final text
    # ----------------------------------------------------

    failed_result = engine.build_response(
        "Test",
        {
            "success": False,
            "error": "Something went wrong"
        }
    )

    final = engine.final_text(
        failed_result
    )

    assert "Something went wrong" in final

    print(
        "Error final text test passed"
    )

    passed += 1


    # ----------------------------------------------------
    # 19. Status
    # ----------------------------------------------------

    status = engine.status()

    assert status["engine"] == ENGINE_NAME
    assert status["version"] == ENGINE_VERSION
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
            "RESPONSE ENGINE TEST PASSED ✅"
        )

        return True

    print(
        "RESPONSE ENGINE TEST FAILED ❌"
    )

    return False


# ========================================================
# RUN DIRECTLY
# ========================================================

if __name__ == "__main__":

    run_self_test()