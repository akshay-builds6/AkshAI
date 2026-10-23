# ================================================================
# AkshAI - PROFESSIONAL BRAIN
# Single-source natural-language router
# Developer: Akshay Yadav
# ================================================================

from dataclasses import dataclass, asdict
import re
import math
import json
import urllib.parse
import urllib.request
from html import unescape


@dataclass
class BrainResult:
    success: bool = True
    query: str = ""
    answer: str = ""
    intent: str = ""
    engine: str = "brain"
    confidence: float = 0.0
    language: str = "english"
    corrected_query: str = ""
    needs_confirmation: bool = False
    suggestion: str = ""
    engines_tried: list = None
    data: dict = None
    error: str = ""

    def __post_init__(self):
        if self.engines_tried is None:
            self.engines_tried = []
        if self.data is None:
            self.data = {}

    def to_dict(self):
        return asdict(self)


class Brain:
    """Central AkshAI understanding + routing layer.

    main.py owns startup/input/output. Brain owns natural-language routing.
    Engines are optional: a missing engine never crashes the whole assistant.
    """

    NAME = "AkshAI Brain"
    VERSION = "Professional Integrated"

    def __init__(self, engines=None, user_name="Akshay"):
        self.engines = engines or {}
        self.user_name = user_name or "Akshay"
        self.pending_confirmation = None
        self.last_query = ""
        self.last_answer = ""
        self.last_intent = ""
        self.last_topic = ""
        self.last_language = ""
        self.history = []
        self.max_history = 30

    # ------------------------------------------------------------
    # TEXT / LANGUAGE
    # ------------------------------------------------------------
    @staticmethod
    def clean_text(text):
        return "" if text is None else str(text).strip()

    def normalize_text(self, text):
        text = self.clean_text(text).lower()
        for old, new in {"×": "*", "÷": "/", "−": "-", "–": "-", "—": "-"}.items():
            text = text.replace(old, new)
        return re.sub(r"\s+", " ", text).strip()

    def detect_language(self, text):
        raw = self.clean_text(text)
        if re.search(r"[\u0900-\u097F]", raw):
            return "hindi"
        words = set(re.findall(r"[a-z]+", raw.lower()))
        hindi = {
            "kya", "kaise", "kyu", "kyon", "kyunki", "hai", "hain", "ho",
            "tha", "thi", "mujhe", "mera", "meri", "mere", "aap", "apka",
            "tum", "batao", "btao", "chahiye", "karna", "karo", "krna", "kro",
            "samjhao", "kitna", "kab", "kahan", "wala", "wali", "waale", "nahi",
            "nahin", "haan", "accha", "acha", "theek", "mummy", "papa", "bhai",
            "bored", "mausam", "baarish", "barish", "din", "date", "samay"
        }
        return "hinglish" if len(words & hindi) >= 2 else "english"

    # ------------------------------------------------------------
    # TYPO CONFIRMATION
    # ------------------------------------------------------------
    TYPO_MAP = {
        r"\bdevelopet\b": "developer",
        r"\bdevelopar\b": "developer",
        r"\bdevoloper\b": "developer",
        r"\bwhatsap\b": "whatsapp",
        r"\bwhatsaap\b": "whatsapp",
        r"\byoutub\b": "youtube",
        r"\binstgram\b": "instagram",
        r"\bweathr\b": "weather",
        r"\bexplan\b": "explain",
        r"\bexplaning\b": "explaining",
        r"\bthermodynamcs\b": "thermodynamics",
        r"\bnucelus\b": "nucleus",
        r"\belectrostatc\b": "electrostatic",
        r"\bgravitational forcee\b": "gravitational force",
        r"\bnoifa\b": "noida",
        r"\bnoidaa\b": "noida",
        r"\bghaziabaad\b": "ghaziabad",
    }

    def normalize_typos(self, text):
        original = self.clean_text(text)
        corrected = original
        for pattern, replacement in self.TYPO_MAP.items():
            corrected = re.sub(pattern, replacement, corrected, flags=re.I)
        return corrected, (corrected if corrected != original else "")

    def ask_confirmation(self, original, suggestion):
        self.pending_confirmation = {"original": original, "suggestion": suggestion}
        return BrainResult(
            success=True, query=original,
            answer=f"Did you mean **{suggestion}**?",
            intent="confirmation", engine="brain", confidence=0.96,
            language=self.detect_language(original), corrected_query=suggestion,
            needs_confirmation=True, suggestion=suggestion,
            engines_tried=["brain"]
        )

    def handle_confirmation(self, query):
        if not self.pending_confirmation:
            return None
        q = self.normalize_text(query)
        yes = {"yes", "yeah", "yep", "haan", "ha", "ji", "correct", "right", "yes please"}
        no = {"no", "nope", "nah", "nahi", "nahin"}
        if q in yes:
            suggestion = self.pending_confirmation["suggestion"]
            self.pending_confirmation = None
            return self.process(suggestion)
        if q in no:
            original = self.pending_confirmation["original"]
            self.pending_confirmation = None
            return self.final_answer(
                original,
                intent="clarification",
                answer="👍 Okay. I won't assume what you meant. Please tell me what you meant.",
                confidence=0.96,
            )
        return None

    # ------------------------------------------------------------
    # RESULT ADAPTER
    # ------------------------------------------------------------
    @staticmethod
    def _success_flag(result):
        if result is None:
            return False
        if isinstance(result, dict) and result.get("success") is False:
            return False
        try:
            if getattr(result, "success", True) is False:
                return False
        except Exception:
            pass
        return True

    @staticmethod
    def extract_text(result):
        if result is None:
            return ""
        if isinstance(result, str):
            return result.strip()
        keys = ("answer", "response", "text", "message", "content", "formatted", "output")
        if isinstance(result, dict):
            for key in keys:
                value = result.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
            data = result.get("data")
            if isinstance(data, dict):
                for key in keys:
                    value = data.get(key)
                    if isinstance(value, str) and value.strip():
                        return value.strip()
            return ""
        for key in keys + ("result", "value"):
            try:
                value = getattr(result, key, None)
                if isinstance(value, str) and value.strip():
                    return value.strip()
                if isinstance(value, (int, float)):
                    return str(value)
            except Exception:
                pass
        return ""

    @staticmethod
    def extract_data(result):
        if isinstance(result, dict):
            return result.get("data", result) if isinstance(result.get("data", result), dict) else {}
        try:
            value = getattr(result, "data", {})
            return value if isinstance(value, dict) else {}
        except Exception:
            return {}

    def _is_usable(self, result, source=""):
        if not self._success_flag(result):
            return False
        text = self.extract_text(result)
        if not text:
            return False
        low = self.normalize_text(text)
        bad = {
            "ai unavailable",
            "no reliable answer",
            "i don't know",
            "i do not know",
            "google search",
            "please click here if you are not redirected",
        }
        if any(item in low for item in bad):
            return False
        # ai_engine deliberately returns a fallback result when no provider/key exists.
        if source == "ai_engine":
            source_value = ""
            try:
                source_value = str(getattr(result, "source", "")).lower()
            except Exception:
                if isinstance(result, dict):
                    source_value = str(result.get("source", "")).lower()
            if source_value == "fallback":
                return False
        return True

    def call_engine(self, name, methods, query=None, **kwargs):
        engine = self.engines.get(name)
        if engine is None:
            return None
        for method_name in methods:
            method = getattr(engine, method_name, None)
            if not callable(method):
                continue
            try:
                if query is None:
                    return method(**kwargs) if kwargs else method()
                try:
                    return method(query, **kwargs) if kwargs else method(query)
                except TypeError:
                    return method(query=query, **kwargs) if kwargs else method(query=query)
            except Exception:
                continue
        return None

    def run_text(self, name, methods, query, **kwargs):
        result = self.call_engine(name, methods, query, **kwargs)
        return self.extract_text(result) if self._is_usable(result, name) else ""

    # ------------------------------------------------------------
    # INTENT
    # ------------------------------------------------------------
    def looks_like_math(self, q):
        q = self.normalize_text(q)
        if re.fullmatch(r"[0-9\s.()+\-*/%^,×÷]+", q):
            return True
        if re.search(r"\b(square|cube)\s+(root|of)\b", q):
            return True
        if any(x in q for x in ("calculate ", "solve ", "find the value", "how much is")) and re.search(r"\d", q):
            return True
        if re.search(r"\d\s*(?:\+|\-|\*|/|%|\^|×|÷)\s*\d", q):
            return True
        if re.search(r"\b\d+(?:\.\d+)?\s+(?:plus|minus|times|multiplied by|divided by|percent of)\s+\d", q):
            return True
        return False

    def detect_intent(self, query):
        q = self.normalize_text(query)
        if not q:
            return "empty"

        if self.pending_confirmation and q in {
            "yes", "yeah", "yep", "haan", "ha", "ji",
            "no", "nope", "nahi", "nahin", "nhi"
        }:
            return "confirmation"

        # Route direct emotional disclosures to the local reply engine.
        # Keep this narrow so questions about emotions still use normal routing.
        emotional_disclosure_patterns = (
            r"^(?:i am|i'm|im|i feel|i'm feeling|im feeling|feeling|feel) "
            r"(?:really |very |so |a bit |quite |too )?"
            r"(?:sad|upset|down|lonely|alone|worried|anxious|scared|afraid|angry|mad|frustrated|"
            r"happy|excited|nervous|stressed|overwhelmed|disappointed|hurt|tired|exhausted)\b",
            r"^(?:i have been|i've been|ive been) "
            r"(?:feeling )?(?:sad|upset|lonely|worried|anxious|scared|angry|stressed|overwhelmed)\b",
            r"^(?:mujhe|main|mai) (?:bahut |bohot |kaafi )?"
            r"(?:bura lag raha hai|udaas hoon|udas hu|akela lag raha hai|darr lag raha hai|tension ho rahi hai)\b",
            r"^(?:i am not okay|i'm not okay|im not okay|i am not ok|i'm not ok|im not ok)$",
        )
        if any(re.search(pattern, q, flags=re.I) for pattern in emotional_disclosure_patterns):
            return "conversation"

        # Exact conversational phrases first. This prevents greetings and
        # short social messages from becoming web searches.
        conversation = {
            "hi", "hello", "hey", "hello there", "hey akshai", "hello akshai",
            "hi akshai", "hey aksh", "hello aksh", "good morning",
            "good afternoon", "good evening", "good night", "how are you",
            "how r u", "thanks", "thank you", "sorry", "bye", "goodbye",
            "nothing", "nothing much", "not much", "well", "i am bored",
            "im bored", "i'm bored", "bored", "kuch nahi", "kuch bhi nahi",
            "theek", "okay", "ok", "fine"
        }
        if q in conversation:
            return "conversation"

        action_patterns = [
            r"^(open|launch|start)\s+",
            r"^(call|phone|dial)\s+",
            r"^(send|message|text)\s+",
            r"^whatsapp\s+",
        ]
        if any(re.search(pattern, q) for pattern in action_patterns):
            return "action"

        if self.looks_like_math(q):
            return "calculator"

        weather_words = (
            "weather", "temperature", "forecast", "rain", "raining", "humidity",
            "wind", "aqi", "air quality", "mausam", "baarish", "barish", "garmi", "sardi"
        )
        if any(word in q for word in weather_words):
            return "weather"

        time_exact = {
            "time", "date", "day", "today", "tomorrow", "what time is it",
            "what is the time", "what is today's date", "today's date",
            "todays date", "what day is it"
        }
        if q in time_exact or any(word in q for word in (
            "current time", "time now", "date today", "today's date", "todays date",
            "what day", "which day", "aaj ki date", "aaj ka din", "samay kya", "kitne baje"
        )):
            return "time"

        profile_words = (
            "your developer", "who developed you", "who is your developer", "who made you",
            "who created you", "your creator", "your founder", "who built you", "who is your owner",
            "who are you", "change name", "set my name", "call me", "my name", "what is your name",
            "your name", "akshay yadav", "who is akshay", "about akshay", "developer", "founder"
        )
        if any(word in q for word in profile_words):
            return "profile"

        memory_phrases = (
            "remember",
            "forget",
            "save this",
            "my memory",
            "search memory",
            "search my memory",
            "memory for",
            "yaad rakh",
            "yaad hai",
            "bhool ja",
            "meri memory",
        )
        if any(phrase in q for phrase in memory_phrases):
            return "memory"
        if any(word in q for word in ("make a note", "save a note", "my notes", "show notes", "note this")):
            return "notes"

        knowledge_words = (
            "what is", "what are", "who is", "why", "how does", "explain", "define", "meaning",
            "difference between", "principle", "law", "formula", "force", "energy", "motion",
            "atom", "molecule", "electric", "magnetic", "gravity", "gravitational", "electrostatic",
            "thermodynamics", "nucleus", "proton", "neutron", "electron", "quantum", "relativity",
            "inertia", "pressure", "velocity", "acceleration", "momentum", "work", "power", "heat",
            "chemical", "bonding", "periodic", "photosynthesis", "cell", "vector", "vectors"
        )
        if any(word in q for word in knowledge_words):
            return "knowledge"

        if any(word in q for word in (
            "write", "draft", "application", "letter", "paragraph", "shayari", "poem", "birthday message"
        )):
            return "writing"
        if any(word in q for word in (
            "python", "code", "coding", "program", "programming", "bug", "syntax error", "module not found"
        )):
            return "coding"
        return "ai"

    # ------------------------------------------------------------
    # SPECIALIZED ENGINES
    # ------------------------------------------------------------
    def run_calculator(self, query):
        text = query.strip()
        candidates = [text]
        stripped = re.sub(r"^(what is|calculate|solve|find the value of|how much is)\s+", "", text, flags=re.I).strip()
        if stripped and stripped != text:
            candidates.append(stripped)
        for pattern, repl in (
            (r"^square root of (.+)$", r"sqrt(\1)"),
            (r"^square root (.+)$", r"sqrt(\1)"),
            (r"^cube root of (.+)$", r"cbrt(\1)"),
            (r"^cube root (.+)$", r"cbrt(\1)"),
            (r"^square of (.+)$", r"(\1)^2"),
            (r"^cube of (.+)$", r"(\1)^3"),
            (r"^(.+?)\s+plus\s+(.+)$", r"\1 + \2"),
            (r"^(.+?)\s+minus\s+(.+)$", r"\1 - \2"),
            (r"^(.+?)\s+(?:times|multiplied by)\s+(.+)$", r"\1 * \2"),
            (r"^(.+?)\s+divided by\s+(.+)$", r"\1 / \2"),
        ):
            for candidate in list(candidates):
                converted = re.sub(pattern, repl, candidate, flags=re.I).strip()
                if converted and converted not in candidates:
                    candidates.append(converted)
        for candidate in candidates:
            result = self.call_engine("calculator_engine", ("calculate", "quick_calculate", "answer_query", "answer"), candidate)
            if self._is_usable(result, "calculator_engine"):
                return self.extract_text(result)
        return ""

    def run_weather(self, query):
        return self.run_text("weather_engine", ("answer_query", "get_weather", "fetch_weather"), query)

    def run_time(self, query):
        return self.run_text("time_engine", ("answer_query", "get_current_time", "current_time"), query)

    def run_profile(self, query):
        return self.run_text("profile_engine", ("answer_query", "answer", "get_profile"), query)

    def run_memory(self, query):
        engine = self.engines.get("memory_engine")
        if engine is None:
            return ""

        q = self.normalize_text(query)

        save_phrases = (
            "remember this",
            "remember that",
            "save this memory",
            "save this",
            "yaad rakh",
            "yaad rakhna",
            "isko yaad",
            "ise yaad",
        )

        if any(phrase in q for phrase in save_phrases):
            content = self.clean_text(query)

            result = engine.add(
                content=content,
                category="general",
                importance=3,
            )

            if self._success_flag(result):
                return "Memory saved successfully."

            return (
                self.extract_text(result)
                or "I couldn't save that memory."
            )

        return self.run_text(
            "memory_engine",
            ("search",),
            query,
        )

    def run_notes(self, query):
        return self.run_text("notes_engine", ("answer_query", "search", "get", "add"), query)

    def run_reply(self, query):
        return self.run_text("reply_engine", ("answer_query", "reply", "respond"), query)

    def run_action(self, query):
        return self.run_text("action_engine", ("answer_query", "execute", "handle", "process", "run", "act"), query)

    def run_knowledge(self, query):
        return self.run_text("knowledge_engine", ("answer_query", "answer", "search"), query)

    def run_ai(self, query):
        engine = self.engines.get("ai_engine")
        if engine is None:
            return ""
        context = self.ai_context()
        for method_name in ("answer", "generate", "respond", "ask"):
            method = getattr(engine, method_name, None)
            if not callable(method):
                continue
            for call_style in (1, 2, 3):
                try:
                    if call_style == 1:
                        result = method(query, context=context)
                    elif call_style == 2:
                        result = method(query=query, context=context)
                    else:
                        result = method(query)
                    if self._is_usable(result, "ai_engine"):
                        return self.extract_text(result)
                    break
                except TypeError:
                    continue
                except Exception:
                    break
        return ""

    # ------------------------------------------------------------
    # DIRECT LOCAL FALLBACK KNOWLEDGE
    # ------------------------------------------------------------
    def local_answer(self, query):
        q = self.normalize_text(query)
        if "vector" in q:
            return (
                "### Vectors\n"
                "A vector is a physical/mathematical quantity that has both **magnitude and direction**.\n\n"
                "• Examples: displacement, velocity, acceleration, force, momentum\n"
                "• A scalar has magnitude only.\n"
                "• Vectors can be represented by directed arrows."
            )
        if "gravitational force" in q or q == "gravity" or "force of gravity" in q:
            return (
                "### Gravitational Force 🌍\n"
                "Gravitational force is the attractive force between masses.\n\n"
                "• Near Earth: weight is approximately **F = mg**.\n"
                "• It always acts toward the attracting mass.\n"
                "• It is one of the four fundamental interactions."
            )
        if "electrostatic force" in q or "coulomb" in q:
            return (
                "### Electrostatic Force ⚡\n"
                "Electrostatic force is the force between electric charges.\n\n"
                "• Like charges repel.\n"
                "• Unlike charges attract.\n"
                "• Its magnitude follows Coulomb's law and decreases with the square of separation."
            )
        if "diwali" in q and "2026" in q:
            return "🪔 Diwali in 2026 falls on **8 November 2026 (Sunday)**."
        if any(x in q for x in ("who is akshay yadav", "who is akshay", "about akshay")):
            return (
                "### Akshay Yadav 👨‍💻\n"
                "Akshay Yadav is the **Founder & Developer of AkshAI**.\n\n"
                "• Class 11 PCM student\n"
                "• Coding and programming enthusiast\n"
                "• Dream: become a Fighter Jet Pilot through the NDA path 🇮🇳\n"
                "• Building AkshAI as a personal AI assistant that can learn, think, create and assist."
            )
        return ""

    # ------------------------------------------------------------
    # WEB SEARCH FALLBACK (EXTRACTED, NEVER RAW GOOGLE PAGE)
    # ------------------------------------------------------------
    def direct_web_search(self, query, max_results=5):
        try:
            url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
            req = urllib.request.Request(url, headers={"User-Agent": "AkshAI/Professional"})
            with urllib.request.urlopen(req, timeout=8) as response:
                html = response.read().decode("utf-8", errors="ignore")
            # Pull DuckDuckGo result blocks without requiring external packages.
            blocks = re.findall(r'<div class="result__body".*?</div>\s*</div>', html, flags=re.S | re.I)
            answers = []
            for block in blocks[:max_results]:
                title = re.search(r'class="result__a"[^>]*>(.*?)</a>', block, flags=re.S | re.I)
                snippet = re.search(r'class="result__snippet"[^>]*>(.*?)</a?>', block, flags=re.S | re.I)
                if not snippet:
                    snippet = re.search(r'class="result__snippet"[^>]*>(.*?)</div>', block, flags=re.S | re.I)
                if title:
                    t = re.sub(r"<.*?>", " ", title.group(1))
                    t = re.sub(r"\s+", " ", unescape(t)).strip()
                else:
                    t = ""
                if snippet:
                    s = re.sub(r"<.*?>", " ", snippet.group(1))
                    s = re.sub(r"\s+", " ", unescape(s)).strip()
                else:
                    s = ""
                if t and s:
                    answers.append(f"• **{t}**\n  {s}")
            if answers:
                return "### Web Results 🌐\n\n" + "\n\n".join(answers)
        except Exception:
            pass
        return ""

    def run_web(self, query):
        for name in ("web_engine", "internet_engine"):
            result = self.call_engine(name, ("search_text", "search_web", "search", "answer_query", "get_page_data"), query)
            if self._is_usable(result, name):
                text = self.extract_text(result)
                if "google search" not in self.normalize_text(text):
                    return text
        return self.direct_web_search(query)

    # ------------------------------------------------------------
    # CONVERSATION / FOLLOW-UP
    # ------------------------------------------------------------
    def is_follow_up(self, query):
        q = self.normalize_text(query)
        if not self.last_topic:
            return False
        if q in {"more", "examples", "example", "formula", "formulas", "definition", "meaning", "why", "how", "explain more", "short note", "notes"}:
            return True
        return q.startswith(("more ", "explain more ", "give examples ", "tell me more "))

    def resolve_follow_up(self, query):
        q = self.normalize_text(query)
        if "formula" in q:
            return f"{self.last_topic} formula"
        if "example" in q:
            return f"{self.last_topic} examples"
        if "definition" in q or "meaning" in q:
            return f"{self.last_topic} definition"
        return f"explain {self.last_topic} {query}"

    def extract_topic(self, query):
        q = self.normalize_text(query)
        topics = [
            "gravitational force", "electrostatic force", "electric field", "magnetic field",
            "newton second law", "newton first law", "newton third law", "momentum",
            "kinetic energy", "potential energy", "work", "power", "vectors", "vector",
            "atom", "molecule", "chemical bonding", "binomial theorem", "sequence and series",
            "linear inequalities", "quadratic equation", "motion in a plane", "thermodynamics"
        ]
        for topic in topics:
            if topic in q:
                return topic
        return ""

    def ai_context(self):
        lines = []
        for item in self.history[-8:]:
            lines.append(f"User: {item['query']}\nAkshAI: {item['answer']}")
        return "\n".join(lines)

    def remember_turn(self, query, answer, intent):
        self.last_query = self.clean_text(query)
        self.last_answer = self.clean_text(answer)
        self.last_intent = intent or ""
        self.last_language = self.detect_language(query)
        topic = self.extract_topic(query)
        if topic:
            self.last_topic = topic
        self.history.append({"query": self.last_query, "answer": self.last_answer, "intent": self.last_intent})
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

    # ------------------------------------------------------------
    # FINAL RESULT
    # ------------------------------------------------------------
    def final_answer(self, query, intent="", answer="", engine="brain", confidence=0.0, data=None, engines_tried=None):
        text = self.clean_text(answer)
        success = bool(text)
        if not text:
            text = "🤔 I couldn't get a reliable answer right now. Please try asking in a little more detail."
        return BrainResult(
            success=success, query=self.clean_text(query), answer=text,
            intent=intent or self.detect_intent(query), engine=engine,
            confidence=confidence, language=self.detect_language(query),
            corrected_query=self.clean_text(query), engines_tried=engines_tried or [],
            data=data or {}
        )

    # ------------------------------------------------------------
    # MAIN ROUTER — SINGLE SOURCE OF TRUTH
    # ------------------------------------------------------------
    def process(self, query, **kwargs):
        query = self.clean_text(query)
        if not query:
            return self.final_answer("", "empty", "😊 I'm here. Tell me what you need.", confidence=1.0)

        confirmation = self.handle_confirmation(query)
        if confirmation is not None:
            self.remember_turn(query, confirmation.answer, confirmation.intent)
            return confirmation

        corrected, suggestion = self.normalize_typos(query)
        if suggestion:
            return self.ask_confirmation(query, suggestion)

        intent = self.detect_intent(query)
        tried = []

        # Follow-up gets first chance to use the previous topic.
        if self.is_follow_up(query):
            resolved = self.resolve_follow_up(query)
            tried.append("knowledge_engine")
            answer = self.run_knowledge(resolved)
            if answer:
                result = self.final_answer(query, "follow_up", answer, "knowledge_engine", .96, engines_tried=tried)
                self.remember_turn(query, result.answer, result.intent)
                return result
            answer = self.local_answer(resolved)
            if answer:
                result = self.final_answer(query, "follow_up", answer, "brain", .88, engines_tried=tried)
                self.remember_turn(query, result.answer, result.intent)
                return result

        if intent == "conversation":
            tried.append("reply_engine")
            q = self.normalize_text(query)
            if q in {"well", "fine", "okay", "ok"}:
                answer = "😊 Got it. I'm here with you. Tell me what you're thinking about, or ask me anything."
            elif "bored" in q:
                answer = "😄 Bored? Let's fix that!\n\n• 🎯 Give me a challenge or quiz\n• 🧠 Ask me something interesting\n• 🎮 We can play a simple game\n• ✍️ Create something together\n• 💡 Or just talk — I'm listening."
            else:
                answer = self.run_reply(query) or self.local_conversation(query)
            result = self.final_answer(query, "conversation", answer, "reply_engine", .97, engines_tried=tried)
            self.remember_turn(query, result.answer, result.intent)
            return result

        if intent == "action":
            tried.append("action_engine")
            answer = self.run_action(query)
            if answer:
                result = self.final_answer(query, "action", answer, "action_engine", .96, engines_tried=tried)
                self.remember_turn(query, result.answer, result.intent)
                return result

        if intent == "calculator":
            tried.append("calculator_engine")
            answer = self.run_calculator(query)
            if answer:
                result = self.final_answer(query, "calculator", answer, "calculator_engine", .99, engines_tried=tried)
                self.remember_turn(query, result.answer, result.intent)
                return result

        if intent == "weather":
            tried.append("weather_engine")
            answer = self.run_weather(query)
            if answer:
                result = self.final_answer(query, "weather", answer, "weather_engine", .98, engines_tried=tried)
                self.remember_turn(query, result.answer, result.intent)
                return result

        if intent == "time":
            tried.append("time_engine")
            answer = self.run_time(query)
            if answer:
                result = self.final_answer(query, "time", answer, "time_engine", .98, engines_tried=tried)
                self.remember_turn(query, result.answer, result.intent)
                return result

        if intent == "profile":
            tried.append("profile_engine")
            answer = self.run_profile(query)
            if answer:
                result = self.final_answer(query, "profile", answer, "profile_engine", .98, engines_tried=tried)
                self.remember_turn(query, result.answer, result.intent)
                return result

        if intent == "memory":
            tried.append("memory_engine")
            answer = self.run_memory(query)
            if answer:
                result = self.final_answer(query, "memory", answer, "memory_engine", .95, engines_tried=tried)
                self.remember_turn(query, result.answer, result.intent)
                return result

        if intent == "notes":
            tried.append("notes_engine")
            answer = self.run_notes(query)
            if answer:
                result = self.final_answer(query, "notes", answer, "notes_engine", .95, engines_tried=tried)
                self.remember_turn(query, result.answer, result.intent)
                return result

        if intent == "knowledge":
            # Knowledge engine gets first chance; if it has no answer,
            # continue into the existing AI -> web fallback chain.
            tried.append("knowledge_engine")
            answer = self.run_knowledge(query)
            if answer:
                result = self.final_answer(
                    query, "knowledge", answer, "knowledge_engine", .94,
                    engines_tried=tried
                )
                self.remember_turn(query, result.answer, result.intent)
                return result

            # Deterministic local knowledge can answer known facts, but an
            # empty local answer must not block AI/web fallback.
            local = self.local_answer(query)
            if local:
                result = self.final_answer(
                    query, "knowledge", local, "brain", .92,
                    engines_tried=tried
                )
                self.remember_turn(query, result.answer, result.intent)
                return result

        if intent in {"coding", "writing"}:
            tried.append("ai_engine")
            answer = self.run_ai(query)
            if answer:
                result = self.final_answer(query, intent, answer, "ai_engine", .93, engines_tried=tried)
                self.remember_turn(query, result.answer, result.intent)
                return result
            # A failed AI provider must not be turned into a fake answer.

        # Deterministic local knowledge gets priority over an unavailable or
        # low-quality AI provider. This protects known answers such as profile
        # and calendar facts from generic AI fallback text.
        local = self.local_answer(query)
        if local:
            result = self.final_answer(query, intent, local, "brain", .92, engines_tried=tried)
            self.remember_turn(query, result.answer, result.intent)
            return result

        # Broad questions: AI first, then extracted web results.
        if "ai_engine" not in tried:
            tried.append("ai_engine")
            answer = self.run_ai(query)
            if answer:
                result = self.final_answer(query, intent, answer, "ai_engine", .90, engines_tried=tried)
                self.remember_turn(query, result.answer, result.intent)
                return result

        tried.append("web_engine")
        answer = self.run_web(query)
        if answer:
            result = self.final_answer(query, "web", answer, "web_engine", .78, engines_tried=tried)
            self.remember_turn(query, result.answer, result.intent)
            return result

        answer = self.local_answer(query)
        result = self.final_answer(query, intent, answer, "brain" if answer else "brain", .55 if answer else .20, engines_tried=tried)
        self.remember_turn(query, result.answer, result.intent)
        return result

    def local_conversation(self, query):
        q = self.normalize_text(query)
        if q in {"hello", "hi", "hey"}:
            return f"👋 Hello, {self.user_name}! 😊 How are you doing?"
        if q in {"thanks", "thank you"}:
            return "You're very welcome! ❤️ I'm always happy to help."
        if q == "sorry":
            return "No worries 😊 You're absolutely fine."
        if q in {"bye", "goodbye"}:
            return "Goodbye! 👋 Take care and keep going. ❤️"
        if "good morning" in q:
            return "🌅 Good morning! I hope today brings you one step closer to your goals. 💙"
        if "good night" in q:
            return "🌙 Good night! Rest well and come back stronger tomorrow. ❤️"
        return "😊 I'm here. Tell me anything."

    def status(self):
        return {
            "name": self.NAME,
            "version": self.VERSION,
            "configured": bool(self.engines),
            "engine_count": len(self.engines),
            "history_count": len(self.history),
            "pending_confirmation": bool(self.pending_confirmation),
            "last_intent": self.last_intent,
            "last_topic": self.last_topic,
        }


# ------------------------------------------------------------
# Module-level compatibility API
# ------------------------------------------------------------
_default_brain = None


def configure_brain(engines=None, user_name="Akshay"):
    global _default_brain
    _default_brain = Brain(engines=engines or {}, user_name=user_name)
    return _default_brain


def get_brain():
    global _default_brain
    if _default_brain is None:
        _default_brain = Brain()
    return _default_brain


def process_brain(query, **kwargs):
    return get_brain().process(query, **kwargs)


def ask_brain(query, **kwargs):
    return get_brain().process(query, **kwargs)


def run_brain(query, **kwargs):
    return get_brain().process(query, **kwargs)


def brain_status():
    return get_brain().status()
