"""
AkshAI - Context Engine v1.0
--------------------------------
Purpose:
- Maintain short-term conversation context.
- Track recent user/AI messages.
- Track current topic.
- Track language.
- Track entities/details mentioned in conversation.
- Resolve basic references such as:
    "kal"
    "wahan"
    "ye"
    "woh"
    "same"
    "iske baare mein"
- Provide clean context to Brain and AI Engine.

Important:
Context Engine is NOT the AI brain.
It stores and organizes context so Brain/AI can understand
the conversation better.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import re


# ============================================================
# MESSAGE
# ============================================================

@dataclass
class ContextMessage:
    role: str
    content: str
    timestamp: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )

    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
        }


# ============================================================
# CONTEXT ENGINE
# ============================================================

class ContextEngine:
    """
    Short-term conversation context manager.

    It does NOT permanently remember everything.
    Permanent information will later be handled by Memory Engine.
    """

    def __init__(
        self,
        max_messages: int = 20,
        max_context_chars: int = 12000
    ):
        self.max_messages = max(1, max_messages)
        self.max_context_chars = max(1000, max_context_chars)

        self.messages: List[ContextMessage] = []

        self.current_topic: Optional[str] = None
        self.previous_topic: Optional[str] = None

        self.language: str = "unknown"

        self.entities: Dict[str, Any] = {}

        self.last_user_message: str = ""
        self.last_assistant_message: str = ""

        self.turn_count: int = 0

    # ========================================================
    # BASIC TEXT HELPERS
    # ========================================================

    @staticmethod
    def clean_text(text: Any) -> str:
        if text is None:
            return ""

        return " ".join(str(text).strip().split())

    # ========================================================
    # LANGUAGE DETECTION
    # ========================================================

    @staticmethod
    def detect_language(text: str) -> str:
        """
        Lightweight language detection.

        Returns:
            hindi
            english
            hinglish
            unknown
        """

        text = ContextEngine.clean_text(text)

        if not text:
            return "unknown"

        devanagari = len(
            re.findall(r"[\u0900-\u097F]", text)
        )

        english_words = re.findall(
            r"\b[a-zA-Z]+\b",
            text
        )

        english_count = len(english_words)

        hindi_words = {
            "hai", "hain", "ho", "ka", "ki", "ke",
            "kya", "kyu", "kyon", "mera", "meri",
            "mere", "mujhe", "aap", "apka", "ye",
            "woh", "aur", "me", "mein", "se",
            "ko", "par", "bhi", "nahi", "nahin",
            "chahiye", "batao", "bata", "karna",
            "karo", "kr", "krna", "ab", "kal",
            "aaj", "wala", "wali"
        }

        lower_words = {
            word.lower()
            for word in english_words
        }

        hinglish_hits = len(
            lower_words.intersection(hindi_words)
        )

        if devanagari > 0 and english_count > 0:
            return "hinglish"

        if devanagari > 0:
            return "hindi"

        if hinglish_hits > 0:
            return "hinglish"

        if english_count > 0:
            return "english"

        return "unknown"

    # ========================================================
    # TOPIC DETECTION
    # ========================================================

    @staticmethod
    def detect_topic(text: str) -> Optional[str]:
        """
        Lightweight topic detection.

        This is only a hint for Brain.
        The AI Engine will later perform deeper understanding.
        """

        text = ContextEngine.clean_text(text).lower()

        if not text:
            return None

        topic_keywords = {
            "physics": [
                "physics",
                "force",
                "motion",
                "velocity",
                "acceleration",
                "newton",
                "momentum",
                "energy",
                "electricity",
                "magnetic",
                "gravity",
            ],

            "chemistry": [
                "chemistry",
                "atom",
                "molecule",
                "reaction",
                "organic",
                "inorganic",
                "mole",
                "periodic table",
            ],

            "mathematics": [
                "math",
                "mathematics",
                "algebra",
                "calculus",
                "geometry",
                "trigonometry",
                "probability",
                "permutation",
                "combination",
                "equation",
            ],

            "jee": [
                "jee",
                "mains",
                "advanced",
                "percentile",
                "rank",
                "nta",
            ],

            "coding": [
                "python",
                "code",
                "coding",
                "program",
                "programming",
                "bug",
                "error",
                "function",
                "class",
                "variable",
            ],

            "weather": [
                "weather",
                "temperature",
                "rain",
                "humidity",
                "forecast",
                "wind",
            ],

            "school": [
                "school",
                "teacher",
                "class",
                "homework",
                "exam",
                "principal",
                "application",
                "attendance",
            ],

            "time": [
                "time",
                "date",
                "today",
                "tomorrow",
                "yesterday",
            ],

            "general": [
                "what",
                "why",
                "how",
                "explain",
                "meaning",
                "tell",
            ],
        }

        scores: Dict[str, int] = {}

        for topic, keywords in topic_keywords.items():
            score = 0

            for keyword in keywords:
                if keyword in text:
                    score += 1

            if score:
                scores[topic] = score

        if not scores:
            return None

        return max(
            scores,
            key=scores.get
        )

    # ========================================================
    # ENTITY EXTRACTION
    # ========================================================

    @staticmethod
    def extract_entities(text: str) -> Dict[str, str]:
        """
        Extract simple useful entities.

        This is intentionally lightweight.
        AI/LLM will handle deep entity understanding later.
        """

        text = ContextEngine.clean_text(text)

        if not text:
            return {}

        entities = {}

        # Common location patterns
        location_patterns = [
            r"\bin ([A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+)*)",
            r"\bat ([A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+)*)",
        ]

        for pattern in location_patterns:
            match = re.search(pattern, text)

            if match:
                entities["location"] = match.group(1)
                break

        # Numbers
        number_match = re.search(
            r"\b\d+(?:\.\d+)?\b",
            text
        )

        if number_match:
            entities["number"] = number_match.group(0)

        return entities

    # ========================================================
    # ADD MESSAGE
    # ========================================================

    def add_message(
        self,
        role: str,
        content: str
    ) -> ContextMessage:

        content = self.clean_text(content)

        if not content:
            return ContextMessage(
                role=role,
                content=""
            )

        message = ContextMessage(
            role=role,
            content=content
        )

        self.messages.append(message)

        if role == "user":
            self.last_user_message = content
            self.turn_count += 1

            detected_language = self.detect_language(content)

            if detected_language != "unknown":
                self.language = detected_language

            detected_topic = self.detect_topic(content)

            if detected_topic:
                if (
                    self.current_topic
                    and detected_topic != self.current_topic
                ):
                    self.previous_topic = self.current_topic

                self.current_topic = detected_topic

            new_entities = self.extract_entities(content)

            if new_entities:
                self.entities.update(new_entities)

        elif role == "assistant":
            self.last_assistant_message = content

        self._trim_context()

        return message

    # ========================================================
    # USER MESSAGE
    # ========================================================

    def add_user_message(
        self,
        content: str
    ) -> ContextMessage:

        return self.add_message(
            "user",
            content
        )

    # ========================================================
    # ASSISTANT MESSAGE
    # ========================================================

    def add_assistant_message(
        self,
        content: str
    ) -> ContextMessage:

        return self.add_message(
            "assistant",
            content
        )

    # ========================================================
    # CONTEXT TRIMMING
    # ========================================================

    def _trim_context(self) -> None:
        """
        Keep context within safe limits.
        """

        if len(self.messages) > self.max_messages:
            self.messages = self.messages[
                -self.max_messages:
            ]

        while (
            self.get_context_character_count()
            > self.max_context_chars
            and len(self.messages) > 1
        ):
            self.messages.pop(0)

    # ========================================================
    # CONTEXT CHARACTER COUNT
    # ========================================================

    def get_context_character_count(self) -> int:
        return sum(
            len(message.content)
            for message in self.messages
        )

    # ========================================================
    # RECENT MESSAGES
    # ========================================================

    def get_recent_messages(
        self,
        limit: int = 10
    ) -> List[Dict[str, str]]:

        limit = max(1, limit)

        return [
            message.to_dict()
            for message in self.messages[-limit:]
        ]

    # ========================================================
    # CONVERSATION TEXT
    # ========================================================

    def get_conversation_text(
        self,
        limit: int = 10
    ) -> str:

        recent = self.messages[-max(1, limit):]

        lines = []

        for message in recent:
            role = message.role.capitalize()

            lines.append(
                f"{role}: {message.content}"
            )

        return "\n".join(lines)

    # ========================================================
    # REFERENCE RESOLUTION
    # ========================================================

    def resolve_reference(self, text: str) -> str:
        """
        Resolve simple conversational references.

        Example:

            User:
                Delhi ka weather batao

            User:
                Aur kal?

        Context can provide:

            "kal" -> tomorrow relative to current topic.

        This does NOT perform date calculation.
        Time Engine will handle actual dates later.
        """

        text = self.clean_text(text)

        if not text:
            return text

        lower = text.lower()

        reference_words = {
            "ye": "current subject",
            "yeh": "current subject",
            "woh": "previous subject",
            "vo": "previous subject",
            "iska": "current subject",
            "iske": "current subject",
            "isey": "current subject",
            "uska": "previous subject",
            "uske": "previous subject",
            "same": "same subject",
            "wahi": "same subject",
            "again": "same subject",
            "phir": "same subject",
        }

        resolved = text

        for word, meaning in reference_words.items():
            pattern = r"\b" + re.escape(word) + r"\b"

            if re.search(pattern, lower):
                if self.current_topic:
                    replacement = (
                        f"{meaning} "
                        f"({self.current_topic})"
                    )

                    resolved = re.sub(
                        pattern,
                        replacement,
                        resolved,
                        count=1,
                        flags=re.IGNORECASE
                    )

        return resolved

    # ========================================================
    # FOLLOW-UP DETECTION
    # ========================================================

    def is_follow_up(self, text: str) -> bool:
        """
        Detect whether a message is likely a follow-up.
        """

        text = self.clean_text(text).lower()

        if not text:
            return False

        follow_up_words = {
            "and",
            "also",
            "then",
            "again",
            "same",
            "why",
            "how",
            "what about",
            "aur",
            "phir",
            "fir",
            "iske",
            "iska",
            "uska",
            "woh",
            "ye",
            "yeh",
            "kal",
            "aaj",
            "tomorrow",
            "yesterday",
        }

        for word in follow_up_words:
            if " " in word:
                if word in text:
                    return True
            elif re.search(
                r"\b" + re.escape(word) + r"\b",
                text
            ):
                return True

        # Very short messages are often follow-ups.
        if len(text.split()) <= 4 and self.messages:
            return True

        return False

    # ========================================================
    # FULL CONTEXT
    # ========================================================

    def get_context(self) -> Dict[str, Any]:
        """
        Return complete structured context for Brain.
        """

        return {
            "current_topic": self.current_topic,
            "previous_topic": self.previous_topic,
            "language": self.language,
            "entities": dict(self.entities),
            "turn_count": self.turn_count,
            "last_user_message": self.last_user_message,
            "last_assistant_message": self.last_assistant_message,
            "message_count": len(self.messages),
            "context_character_count":
                self.get_context_character_count(),
            "recent_messages":
                self.get_recent_messages(
                    self.max_messages
                ),
        }

    # ========================================================
    # AI CONTEXT
    # ========================================================

    def get_ai_context(self) -> str:
        """
        Create a clean context block for the future AI Engine.

        This is NOT the final AI prompt.
        """

        context = []

        if self.current_topic:
            context.append(
                f"Current topic: {self.current_topic}"
            )

        if self.previous_topic:
            context.append(
                f"Previous topic: {self.previous_topic}"
            )

        if self.language != "unknown":
            context.append(
                f"Conversation language: {self.language}"
            )

        if self.entities:
            context.append(
                f"Known context details: {self.entities}"
            )

        conversation = self.get_conversation_text()

        if conversation:
            context.append(
                "Recent conversation:\n"
                + conversation
            )

        return "\n\n".join(context)

    # ========================================================
    # SET CONTEXT
    # ========================================================

    def set_entity(
        self,
        key: str,
        value: Any
    ) -> None:

        key = self.clean_text(key)

        if not key:
            return

        self.entities[key] = value

    # ========================================================
    # GET ENTITY
    # ========================================================

    def get_entity(
        self,
        key: str,
        default: Any = None
    ) -> Any:

        return self.entities.get(
            key,
            default
        )

    # ========================================================
    # CLEAR
    # ========================================================

    def clear(self) -> None:
        """
        Clear temporary conversation context.
        """

        self.messages.clear()

        self.current_topic = None
        self.previous_topic = None

        self.language = "unknown"

        self.entities.clear()

        self.last_user_message = ""
        self.last_assistant_message = ""

        self.turn_count = 0

    # ========================================================
    # STATUS
    # ========================================================

    def get_status(self) -> Dict[str, Any]:

        return {
            "engine": "context_engine",
            "version": "1.0",
            "status": "ready",
            "messages": len(self.messages),
            "current_topic": self.current_topic,
            "language": self.language,
            "entities": len(self.entities),
            "turn_count": self.turn_count,
        }


# ============================================================
# GLOBAL ENGINE
# ============================================================

context_engine = ContextEngine()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def add_user_message(text: str) -> Dict[str, str]:

    return context_engine.add_user_message(
        text
    ).to_dict()


def add_assistant_message(text: str) -> Dict[str, str]:

    return context_engine.add_assistant_message(
        text
    ).to_dict()


def get_context() -> Dict[str, Any]:

    return context_engine.get_context()


def get_ai_context() -> str:

    return context_engine.get_ai_context()


def detect_language(text: str) -> str:

    return ContextEngine.detect_language(
        text
    )


def detect_topic(text: str) -> Optional[str]:

    return ContextEngine.detect_topic(
        text
    )


def is_follow_up(text: str) -> bool:

    return context_engine.is_follow_up(
        text
    )


def resolve_reference(text: str) -> str:

    return context_engine.resolve_reference(
        text
    )


def clear_context() -> None:

    context_engine.clear()


# ============================================================
# SELF TEST
# ============================================================

def run_context_engine_test() -> bool:

    engine = ContextEngine()

    # --------------------------------------------------------
    # Language tests
    # --------------------------------------------------------

    if engine.detect_language(
        "Hello how are you"
    ) != "english":
        print("FAILED English detection")
        return False

    if engine.detect_language(
        "Aap kaise hain"
    ) != "hinglish":
        print("FAILED Hinglish detection")
        return False

    if engine.detect_language(
        "आप कैसे हैं"
    ) != "hindi":
        print("FAILED Hindi detection")
        return False

    print("Language detection tests passed")

    # --------------------------------------------------------
    # Topic tests
    # --------------------------------------------------------

    if engine.detect_topic(
        "Explain Newton's law of motion"
    ) != "physics":
        print("FAILED Physics topic detection")
        return False

    if engine.detect_topic(
        "Give me Python code"
    ) != "coding":
        print("FAILED Coding topic detection")
        return False

    if engine.detect_topic(
        "What is the weather in Delhi?"
    ) != "weather":
        print("FAILED Weather topic detection")
        return False

    print("Topic detection tests passed")

    # --------------------------------------------------------
    # Message tests
    # --------------------------------------------------------

    engine.add_user_message(
        "Delhi ka weather batao"
    )

    engine.add_assistant_message(
        "Delhi mein weather clear hai."
    )

    if len(engine.messages) != 2:
        print("FAILED message storage")
        return False

    if engine.last_user_message != (
        "Delhi ka weather batao"
    ):
        print("FAILED last user message")
        return False

    print("Message storage tests passed")

    # --------------------------------------------------------
    # Context topic
    # --------------------------------------------------------

    if engine.current_topic != "weather":
        print("FAILED current topic")
        return False

    # --------------------------------------------------------
    # Follow-up
    # --------------------------------------------------------

    if not engine.is_follow_up("Aur kal?"):
        print("FAILED follow-up detection")
        return False

    print("Follow-up detection tests passed")

    # --------------------------------------------------------
    # Reference resolution
    # --------------------------------------------------------

    resolved = engine.resolve_reference(
        "Aur ye?"
    )

    if "weather" not in resolved.lower():
        print("FAILED reference resolution")
        return False

    print("Reference resolution tests passed")

    # --------------------------------------------------------
    # Entity
    # --------------------------------------------------------

    engine.set_entity(
        "location",
        "Delhi"
    )

    if engine.get_entity(
        "location"
    ) != "Delhi":
        print("FAILED entity storage")
        return False

    print("Entity tests passed")

    # --------------------------------------------------------
    # AI context
    # --------------------------------------------------------

    ai_context = engine.get_ai_context()

    if "weather" not in ai_context.lower():
        print("FAILED AI context generation")
        return False

    if "Delhi" not in ai_context:
        print("FAILED entity context")
        return False

    print("AI context generation passed")

    # --------------------------------------------------------
    # Status
    # --------------------------------------------------------

    status = engine.get_status()

    if status["status"] != "ready":
        print("FAILED status")
        return False

    print("Status test passed")

    # --------------------------------------------------------
    # Clear
    # --------------------------------------------------------

    engine.clear()

    if engine.messages:
        print("FAILED context clear")
        return False

    if engine.current_topic is not None:
        print("FAILED topic clear")
        return False

    print("Clear test passed")

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    print("CONTEXT ENGINE TEST PASSED ✅")

    return True


# ============================================================
# DIRECT EXECUTION
# ============================================================

if __name__ == "__main__":
    run_context_engine_test()     