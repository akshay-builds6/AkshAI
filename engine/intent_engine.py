"""
AkshAI Intent Engine v1.0
---------------------------------
Natural-language intent and language detection engine.

Standard library only.
"""

from dataclasses import dataclass, field
import re


# ============================================================
# INTENT RESULT
# ============================================================

@dataclass
class IntentResult:
    success: bool
    intent: str
    topic: str
    confidence: float
    language: str
    entities: list = field(default_factory=list)
    target_engine: str = ""
    is_follow_up: bool = False
    is_question: bool = False
    urgency: str = "normal"
    original_text: str = ""
    error: str = ""

    def to_dict(self):
        return {
            "success": self.success,
            "intent": self.intent,
            "topic": self.topic,
            "confidence": self.confidence,
            "language": self.language,
            "entities": self.entities,
            "target_engine": self.target_engine,
            "is_follow_up": self.is_follow_up,
            "is_question": self.is_question,
            "urgency": self.urgency,
            "original_text": self.original_text,
            "error": self.error,
        }


# ============================================================
# INTENT ENGINE
# ============================================================

class IntentEngine:

    def __init__(self):

        self.intent_priority = [
            "exit",
            "greeting",
            "coding",
            "calculator",
            "weather",
            "search",
            "memory",
            "notes",
            "writing",
            "comparison",
            "planning",
            "explanation",
            "profile",
            "time",
            "question",
            "general",
        ]

        # ----------------------------------------------------
        # STRONG INTENT PHRASES
        # ----------------------------------------------------

        self.strong_intent_phrases = {

            "coding": [
                "code banao",
                "code bana do",
                "program banao",
                "program bana do",
                "python code",
                "python ka code",
                "coding karo",
                "coding karni hai",
                "app banao",
                "app bana do",
                "website banao",
                "website bana do",
                "script banao",
                "script bana do",
                "function banao",
                "function bana do",
                "class banao",
                "class bana do",
                "debug karo",
                "debug kar do",
                "fix this code",
                "fix the code",
                "write code",
                "write a program",
                "make a program",
                "create an app",
            ],

            "calculator": [
                "calculate",
                "calculate karo",
                "calculate kar do",
                "solve this calculation",
                "solve calculation",
                "hisab karo",
                "hisab laga do",
                "percentage nikal",
                "percent nikal",
            ],

            "weather": [
                "weather batao",
                "weather check karo",
                "mausam batao",
                "mausam kaisa hai",
                "aaj ka mausam",
                "kal ka mausam",
                "temperature batao",
                "baarish hogi",
                "barish hogi",
            ],

            "search": [
                "search karo",
                "search kar do",
                "google par search",
                "google pe search",
                "internet par search",
                "online search",
                "latest news",
                "latest information",
                "latest update",
                "web par search",
            ],

            "memory": [
                "yaad rakhna",
                "yaad rakh lo",
                "yaad rakhna ye",
                "remember this",
                "remember that",
                "remember it",
                "memory mein save",
                "memory me save",
                "save this in memory",
                "bhoolna mat",
            ],

            "writing": [
                "message likho",
                "message likh do",
                "application likho",
                "application likh do",
                "letter likho",
                "letter likh do",
                "paragraph likho",
                "paragraph likh do",
                "essay likho",
                "essay likh do",
                "shayari banao",
                "shayari likho",
                "caption banao",
                "caption likho",
                "email likho",
                "email likh do",
                "write a message",
                "write an email",
                "write a letter",
            ],

            "comparison": [
                "difference batao",
                "difference bata do",
                "compare karo",
                "comparison karo",
                "compare kar do",
                "difference between",
                "farak batao",
                "farak kya hai",
            ],

            "explanation": [
                "samjha do",
                "samjhao",
                "explain karo",
                "explain kar do",
                "explain this",
                "kaise kaam karta",
                "kaise kaam karti",
                "iska meaning",
                "iska matlab",
                "concept samjha do",
                "concept batao",
            ],

            "planning": [
                "plan banao",
                "plan bana do",
                "schedule banao",
                "schedule bana do",
                "timetable banao",
                "roadmap banao",
                "study plan",
                "study schedule",
                "routine banao",
                "routine bana do",
            ],
        }

        # ----------------------------------------------------
        # INTENT KEYWORDS
        # ----------------------------------------------------

        self.intent_keywords = {

            "greeting": [
                "hello",
                "hi",
                "hey",
                "hii",
                "hiii",
                "namaste",
                "namaskar",
                "good morning",
                "good afternoon",
                "good evening",
                "good night",
            ],

            "exit": [
                "bye",
                "goodbye",
                "exit",
                "quit",
                "close",
                "band karo",
                "band kar do",
            ],

            "memory": [
                "remember",
                "memory",
                "yaad",
                "bhool",
                "save",
                "store",
            ],

            "notes": [
                "note",
                "notes",
                "notepad",
                "likh ke rakho",
                "note kar",
                "note karlo",
            ],

            "profile": [
                "profile",
                "mera naam",
                "my name",
                "mere baare",
                "about me",
                "meri information",
            ],

            "weather": [
                "weather",
                "mausam",
                "temperature",
                "rain",
                "baarish",
                "barish",
                "forecast",
                "humidity",
                "wind",
            ],

            "time": [
                "time",
                "samay",
                "kitne baje",
                "what time",
                "clock",
                "date",
                "tarikh",
            ],

            "calculator": [
                "calculate",
                "calculator",
                "plus",
                "minus",
                "multiply",
                "divide",
                "percentage",
                "percent",
                "average",
                "square",
                "cube",
                "sqrt",
                "factorial",
                "gcd",
                "lcm",
                "kitna",
                "kitni",
                "kitne",
                "hisab",
            ],

            "search": [
                "search",
                "google",
                "internet",
                "online",
                "web",
                "latest",
                "news",
                "find",
                "lookup",
            ],

            "coding": [
                "code",
                "coding",
                "python",
                "java",
                "javascript",
                "program",
                "programming",
                "script",
                "function",
                "class",
                "debug",
                "bug",
                "api",
                "html",
                "css",
            ],

            "writing": [
                "write",
                "writing",
                "likho",
                "likh",
                "message",
                "application",
                "letter",
                "email",
                "essay",
                "paragraph",
                "shayari",
                "caption",
                "bio",
            ],

            "explanation": [
                "explain",
                "explanation",
                "samjha",
                "samjhao",
                "concept",
                "meaning",
                "matlab",
                "why",
                "how",
                "kaise",
                "define",
                "definition",
            ],

            "comparison": [
                "compare",
                "comparison",
                "difference",
                "difference between",
                "vs",
                "versus",
                "farak",
                "better",
                "best",
            ],

            "planning": [
                "plan",
                "planning",
                "schedule",
                "timetable",
                "roadmap",
                "routine",
                "strategy",
                "goal",
            ],

            "question": [
                "what",
                "why",
                "how",
                "when",
                "where",
                "who",
                "which",
                "can",
                "could",
                "should",
                "would",
                "kya",
                "kyun",
                "kaise",
                "kab",
                "kahan",
                "kaun",
                "kis",
                "kitna",
                "kitni",
                "kitne",
            ],
        }

        # ----------------------------------------------------
        # TOPIC KEYWORDS
        # ----------------------------------------------------

        self.topic_keywords = {

            "physics": [
                "physics",
                "force",
                "motion",
                "velocity",
                "acceleration",
                "momentum",
                "energy",
                "work",
                "power",
                "gravity",
                "newton",
                "friction",
                "wave",
                "current",
                "voltage",
                "electric",
                "magnetic",
            ],

            "chemistry": [
    "chemistry",
    "chemical",
    "atom",
    "atomic",
    "molecule",
    "molecular",
    "mole",
    "element",
    "compound",
    "reaction",
    "reactant",
    "product",
    "organic",
    "inorganic",
    "acid",
    "base",
    "salt",
    "periodic",
    "periodic table",
    "bond",
    "bonding",
    "ionic",
    "covalent",
    "metallic",
    "equilibrium",
    "electrochemistry",
    "thermodynamics",
    "stoichiometry",
    "oxidation",
    "reduction",
    "redox",
    "pH",
],

            "mathematics": [
                "math",
                "maths",
                "mathematics",
                "algebra",
                "geometry",
                "trigonometry",
                "calculus",
                "probability",
                "statistics",
                "permutation",
                "combination",
                "binomial",
                "equation",
                "quadratic",
                "sequence",
                "series",
            ],

            "education": [
                "school",
                "class",
                "teacher",
                "exam",
                "test",
                "homework",
                "study",
                "syllabus",
                "ncert",
                "jee",
                "neet",
                "board",
                "student",
                "chapter",
            ],

            "coding": [
                "code",
                "coding",
                "python",
                "java",
                "javascript",
                "program",
                "programming",
                "script",
                "software",
                "app",
                "website",
                "api",
            ],

            "weather": [
                "weather",
                "mausam",
                "temperature",
                "rain",
                "baarish",
                "barish",
                "forecast",
                "humidity",
                "wind",
            ],

            "technology": [
                "technology",
                "tech",
                "computer",
                "mobile",
                "phone",
                "android",
                "iphone",
                "software",
                "hardware",
                "ai",
                "artificial intelligence",
                "internet",
            ],

            "sports": [
                "cricket",
                "football",
                "basketball",
                "tennis",
                "match",
                "player",
                "team",
                "goal",
                "run",
                "wicket",
                "bowling",
                "batting",
            ],

            "travel": [
                "travel",
                "trip",
                "flight",
                "train",
                "hotel",
                "airport",
                "tour",
                "vacation",
                "holiday",
            ],
        }


    # ========================================================
    # NORMALIZE
    # ========================================================

    def normalize_text(self, text):

        if not isinstance(text, str):
            return ""

        text = text.lower().strip()

        replacements = {
            "’": "'",
            "‘": "'",
            "“": '"',
            "”": '"',
            "–": "-",
            "—": "-",
            "×": "*",
            "÷": "/",
            "−": "-",
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        text = re.sub(r"\s+", " ", text)

        return text


    # ========================================================
    # LANGUAGE DETECTION
    # ========================================================

    def detect_language(self, text):

        if not text:
            return "english"

        original = text.strip()
        normalized = self.normalize_text(original)

        # Devanagari
        devanagari_count = len(
            re.findall(r"[\u0900-\u097F]", original)
        )

        latin_count = len(
            re.findall(r"[a-zA-Z]", original)
        )

        if devanagari_count > 0:

            if latin_count > 0:
                return "hinglish"

            return "hindi"

                # Roman Hindi vocabulary
        roman_hindi_words = {
            "aap", "ap", "aapka", "aapki", "aapko", "aapse", "aapne",
            "main", "mein", "mai", "mujhe", "mujh", "mera", "meri", "mere",
            "hum", "ham", "hamara", "hamari", "hume",
            "tum", "tumhara", "tumhari", "tumhe", "tumko",
            "ye", "yeh", "woh", "vo",
            "iska", "iski", "isko", "uska", "uski", "usko",
            "kya", "kyu", "kyun", "kyunki", "kaise", "kaisa", "kaisi",
            "kab", "kahan", "kahaan", "kaun", "kis", "kise", "kisko",
            "hai", "hain", "tha", "thi", "the", "hoga", "hogi", "honge",
            "ho", "hona", "hoti", "hote",
            "kar", "karo", "karna", "karni", "karta", "karte", "karti",
            "kiya", "kiye",
            "bata", "batao", "batana", "bataiye",
            "samajh", "samjha", "samjhao", "samajhna",
            "likho", "likh", "likhna",
            "banao", "banana", "banado",
            "do", "de", "dena", "dedo", "dijiye",
            "chahiye", "chahta", "chahti",
            "accha", "achha", "acha", "acchi", "achhi",
            "bahut", "bohot", "zyada", "kam",
            "abhi", "aaj", "kal", "par", "pe",
            "se", "ko", "ka", "ke", "ki",
            "aur", "ya", "lekin", "magar",
            "phir", "fir", "toh", "to", "bhi",
            "nahi", "nahin", "mat", "haan", "han",
            "apna", "apni", "apne",
            "bhai", "bro", "yaar", "yar",
            "sir", "maam", "mam", "madam",
            "school", "ghar", "dost", "dosti",
            "padhai", "padho", "padna", "parhai",
            "isliye", "iske", "uske",
            "yahan", "wahan",
            "wala", "wali", "waale",
        }

        english_words = {
            "i", "you", "we", "they", "he", "she", "it",
            "this", "that", "these", "those",
            "what", "why", "how", "when", "where",
            "who", "which",
            "can", "could", "should", "would", "will",
            "please", "tell", "explain", "write", "make",
            "create", "calculate", "show", "give", "help",
            "want", "need",
            "weather", "today", "tomorrow",
            "physics", "chemistry", "math", "maths",
            "python", "java", "code", "coding", "program",
            "message", "difference", "compare",
            "search", "internet", "latest", "news",
        }

        words = re.findall(
            r"[a-zA-Z]+",
            normalized
        )

        if not words:
            return "hindi"

        hindi_hits = sum(
            1
            for word in words
            if word in roman_hindi_words
        )

        english_hits = sum(
            1
            for word in words
            if word in english_words
        )

        total_words = len(words)

        hindi_ratio = hindi_hits / total_words
        english_ratio = english_hits / total_words

        # Clear English + Roman Hindi mixture
        if hindi_hits >= 1 and english_hits >= 1:
            return "hinglish"

        # Strong Roman Hindi
        if hindi_hits >= 2:
            return "hindi"

        # Hindi ratio
        if hindi_ratio >= 0.20:
            return "hindi"

        # English ratio
        if english_ratio >= 0.40:
            return "english"

        # Hindi-style word endings
        hindi_patterns = [
            r"\b\w+ao\b",
            r"\b\w+o\b",
            r"\b\w+na\b",
            r"\b\w+ni\b",
            r"\b\w+ga\b",
            r"\b\w+gi\b",
            r"\b\w+ge\b",
        ]

        pattern_hits = 0

        for pattern in hindi_patterns:
            if re.search(
                pattern,
                normalized
            ):
                pattern_hits += 1

        if pattern_hits >= 2:
            return "hindi"

        if pattern_hits >= 1 and hindi_hits >= 1:
            return "hinglish"

        return "english"


    # ========================================================
    # QUESTION DETECTION
    # ========================================================

    def is_question(self, text):

        normalized = self.normalize_text(text)

        if not normalized:
            return False

        if "?" in text:
            return True

        question_words = [
            "what",
            "why",
            "how",
            "when",
            "where",
            "who",
            "which",
            "can you",
            "could you",
            "kya",
            "kyun",
            "kaise",
            "kab",
            "kahan",
            "kaun",
            "kis",
            "kitna",
            "kitni",
            "kitne",
        ]

        for word in question_words:
            if (
                normalized.startswith(word + " ")
                or normalized == word
                or (" " + word + " ") in normalized
            ):
                return True

        return False


    # ========================================================
    # FOLLOW-UP DETECTION
    # ========================================================

    def detect_follow_up(self, text):

        normalized = self.normalize_text(text)

        follow_up_phrases = [
            "aur batao",
            "aur bata",
            "aur explain",
            "thoda aur",
            "detail mein",
            "details mein",
            "same",
            "iske baare mein",
            "is topic par",
            "ye wala",
            "woh wala",
            "fir se",
            "phir se",
            "again",
            "continue",
            "next",
            "also",
            "more",
            "what about",
        ]

        return any(
            phrase in normalized
            for phrase in follow_up_phrases
        )


    # ========================================================
    # TOPIC DETECTION
    # ========================================================

    def detect_topic(self, text):

        normalized = self.normalize_text(text)

        if not normalized:
            return "general"

        scores = {}

        for topic, keywords in self.topic_keywords.items():

            score = 0

            for keyword in keywords:

                if " " in keyword:

                    if keyword in normalized:
                        score += 2

                else:

                    if re.search(
                        r"\b" + re.escape(keyword) + r"\b",
                        normalized
                    ):
                        score += 1

            scores[topic] = score

        best_topic = max(
            scores,
            key=scores.get
        )

        if scores[best_topic] == 0:
            return "general"

        return best_topic


    # ========================================================
    # STRONG PHRASE SCORING
    # ========================================================

    def score_strong_phrases(self, text):

        normalized = self.normalize_text(text)

        scores = {}

        for intent, phrases in self.strong_intent_phrases.items():

            score = 0

            for phrase in phrases:

                if phrase in normalized:
                    score += 10

            scores[intent] = score

        return scores


    # ========================================================
    # INTENT SCORING
    # ========================================================

    def score_intents(self, text):

        normalized = self.normalize_text(text)

        scores = {
            intent: 0
            for intent in self.intent_keywords
        }

        strong_scores = self.score_strong_phrases(
            normalized
        )

        for intent, score in strong_scores.items():
            scores[intent] += score

        for intent, keywords in self.intent_keywords.items():

            for keyword in keywords:

                if " " in keyword:

                    if keyword in normalized:
                        scores[intent] += 2

                else:

                    if re.search(
                        r"\b" + re.escape(keyword) + r"\b",
                        normalized
                    ):
                        scores[intent] += 1

        # Coding priority
        if (
            "code" in normalized
            or "coding" in normalized
            or "program" in normalized
        ):
            scores["coding"] += 5

        # Writing priority
        if (
            "message likh" in normalized
            or "application likh" in normalized
            or "letter likh" in normalized
            or "email likh" in normalized
            or "shayari" in normalized
        ):
            scores["writing"] += 5

        # Explanation priority
        if (
            "samjha do" in normalized
            or "samjhao" in normalized
            or "explain" in normalized
            or "concept" in normalized
        ):
            scores["explanation"] += 4

        return scores


    # ========================================================
    # INTENT DETECTION
    # ========================================================

    def detect_intent(self, text):

        normalized = self.normalize_text(text)

        if not normalized:
            return "general"

        greeting_phrases = [
            "hello",
            "hi",
            "hey",
            "hii",
            "hiii",
            "namaste",
            "namaskar",
            "good morning",
            "good afternoon",
            "good evening",
            "good night",
        ]

        if normalized in greeting_phrases:
            return "greeting"

        exit_phrases = [
            "bye",
            "goodbye",
            "exit",
            "quit",
            "close",
            "band karo",
            "band kar do",
        ]

        if normalized in exit_phrases:
            return "exit"

        scores = self.score_intents(normalized)

        best_score = max(
            scores.values()
        )

        if best_score <= 0:
            return "general"

        candidates = [
            intent
            for intent, score in scores.items()
            if score == best_score
        ]

        for priority_intent in self.intent_priority:

            if priority_intent in candidates:
                return priority_intent

        return candidates[0]


    # ========================================================
    # CONFIDENCE
    # ========================================================

    def calculate_confidence(self, text, intent):

        if not text:
            return 0.0

        scores = self.score_intents(text)

        best_score = scores.get(
            intent,
            0
        )

        if best_score <= 0:
            return 0.25

        sorted_scores = sorted(
            scores.values(),
            reverse=True
        )

        second_score = (
            sorted_scores[1]
            if len(sorted_scores) > 1
            else 0
        )

        if best_score >= 10:
            confidence = 0.98
        elif best_score >= 7:
            confidence = 0.94
        elif best_score >= 5:
            confidence = 0.88
        elif best_score >= 3:
            confidence = 0.78
        else:
            confidence = 0.65

        if second_score >= best_score - 1:
            confidence -= 0.08

        return round(
            max(
                0.0,
                min(1.0, confidence)
            ),
            2
        )


    # ========================================================
    # ENTITY EXTRACTION
    # ========================================================

    def extract_entities(self, text):

        normalized = self.normalize_text(text)

        entities = []

        location_patterns = [
            r"\bin ([A-Za-z]+(?: [A-Za-z]+)*)",
        ]

        for pattern in location_patterns:

            matches = re.findall(
                pattern,
                text,
                flags=re.IGNORECASE
            )

            for match in matches:

                value = match.strip()

                if value and value not in entities:
                    entities.append(value)

        language_patterns = [
            r"\bpython\b",
            r"\bjava\b",
            r"\bjavascript\b",
            r"\bc\+\+\b",
            r"\bhtml\b",
            r"\bcss\b",
        ]

        for pattern in language_patterns:

            matches = re.findall(
                pattern,
                normalized,
                flags=re.IGNORECASE
            )

            for match in matches:

                if match not in entities:
                    entities.append(match)

        subject_patterns = [
            r"\bphysics\b",
            r"\bchemistry\b",
            r"\bmaths?\b",
            r"\bmathematics\b",
        ]

        for pattern in subject_patterns:

            matches = re.findall(
                pattern,
                normalized,
                flags=re.IGNORECASE
            )

            for match in matches:

                if match not in entities:
                    entities.append(match)

        numbers = re.findall(
            r"\b\d+(?:\.\d+)?\b",
            normalized
        )

        for number in numbers:

            if number not in entities:
                entities.append(number)

        return entities


    # ========================================================
    # TARGET ENGINE
    # ========================================================

    def get_target_engine(self, intent):

        mapping = {
            "calculator": "calculator_engine",
            "weather": "weather_engine",
            "search": "internet_engine",

            "coding": "ai_engine",
            "writing": "ai_engine",
            "explanation": "ai_engine",
            "comparison": "ai_engine",
            "planning": "ai_engine",
            "question": "ai_engine",
            "general": "ai_engine",

            "memory": "memory_engine",
            "notes": "notes_engine",
            "profile": "profile_engine",
            "time": "time_engine",

            "greeting": "reply_engine",
            "exit": "command_engine",
        }

        return mapping.get(
            intent,
            "ai_engine"
        )


    # ========================================================
    # URGENCY
    # ========================================================

    def detect_urgency(self, text):

        normalized = self.normalize_text(text)

        urgent_words = [
            "urgent",
            "emergency",
            "jaldi",
            "jaldi se",
            "abhi",
            "immediately",
            "asap",
            "important",
            "critical",
        ]

        medium_words = [
            "quickly",
            "fast",
            "soon",
            "please hurry",
            "jaldi karo",
        ]

        if any(
            word in normalized
            for word in urgent_words
        ):
            return "high"

        if any(
            word in normalized
            for word in medium_words
        ):
            return "medium"

        return "normal"


    # ========================================================
    # COMPLETE ANALYSIS
    # ========================================================

    def analyze(self, text):

        try:

            if not isinstance(text, str):

                return IntentResult(
                    success=False,
                    intent="general",
                    topic="general",
                    confidence=0.0,
                    language="english",
                    original_text="",
                    error="Input must be a string.",
                )

            original_text = text

            normalized = self.normalize_text(
                text
            )

            if not normalized:

                return IntentResult(
                    success=False,
                    intent="general",
                    topic="general",
                    confidence=0.0,
                    language="english",
                    original_text=original_text,
                    error="Empty input.",
                )

            language = self.detect_language(
                original_text
            )

            intent = self.detect_intent(
                normalized
            )

            topic = self.detect_topic(
                normalized
            )

            confidence = self.calculate_confidence(
                normalized,
                intent
            )

            entities = self.extract_entities(
                original_text
            )

            target_engine = self.get_target_engine(
                intent
            )

            is_follow_up = self.detect_follow_up(
                normalized
            )

            is_question = self.is_question(
                original_text
            )

            urgency = self.detect_urgency(
                normalized
            )

            return IntentResult(
                success=True,
                intent=intent,
                topic=topic,
                confidence=confidence,
                language=language,
                entities=entities,
                target_engine=target_engine,
                is_follow_up=is_follow_up,
                is_question=is_question,
                urgency=urgency,
                original_text=original_text,
            )

        except Exception as exc:

            return IntentResult(
                success=False,
                intent="general",
                topic="general",
                confidence=0.0,
                language="english",
                original_text=text,
                error=str(exc),
            )


    # ========================================================
    # STATUS
    # ========================================================

    def get_status(self):

        return {
            "engine": "Intent Engine",
            "version": "1.0",
            "status": "ready",
            "supported_languages": [
                "english",
                "hindi",
                "hinglish",
            ],
            "supported_intents": list(
                self.intent_keywords.keys()
            ),
            "topic_count": len(
                self.topic_keywords
            ),
        }


# ============================================================
# GLOBAL ENGINE
# ============================================================

intent_engine = IntentEngine()


# ============================================================
# QUICK HELPERS
# ============================================================

def analyze_intent(text):
    return intent_engine.analyze(text)


def detect_intent(text):
    return intent_engine.detect_intent(text)


def detect_topic(text):
    return intent_engine.detect_topic(text)


def detect_language(text):
    return intent_engine.detect_language(text)


def quick_intent(text):
    return detect_intent(text)


def quick_topic(text):
    return detect_topic(text)


# ============================================================
# SELF TEST
# ============================================================

def run_tests():

    print("=" * 50)
    print("AkshAI Intent Engine v1.0")
    print("=" * 50)

    passed = 0
    total = 0

    def check(name, condition):

        nonlocal passed, total

        total += 1

        if condition:
            print(f"{name} test passed")
            passed += 1
        else:
            print(f"FAILED {name}")

    # --------------------------------------------------------
    # INTENT TESTS
    # --------------------------------------------------------

    check(
        "Greeting detection",
        detect_intent("Hello AkshAI") == "greeting"
    )

    check(
        "Calculator detection",
        detect_intent("Calculate 25 + 5") == "calculator"
    )

    check(
        "Weather detection",
        detect_intent(
            "Delhi ka weather batao"
        ) == "weather"
    )

    check(
        "Explanation detection",
        detect_intent(
            "Physics ka concept samjha do"
        ) == "explanation"
    )

    check(
        "Coding detection",
        detect_intent(
            "Python mein calculator ka code banao"
        ) == "coding"
    )

    check(
        "Memory detection",
        detect_intent(
            "Mera ye point yaad rakhna"
        ) == "memory"
    )

    check(
        "Writing detection",
        detect_intent(
            "Teacher ke liye message likh do"
        ) == "writing"
    )

    check(
        "Comparison detection",
        detect_intent(
            "Python vs Java ka difference batao"
        ) == "comparison"
    )

    # --------------------------------------------------------
    # LANGUAGE TESTS
    # --------------------------------------------------------

    check(
        "English detection",
        detect_language(
            "Please explain Newton's second law"
        ) == "english"
    )

    check(
        "Hindi detection",
        detect_language(
            "मुझे यह समझा दो"
        ) == "hindi"
    )

    check(
        "Hinglish detection",
        detect_language(
            "Bhai mujhe physics ka ye concept samjha do"
        ) == "hinglish"
    )

    check(
        "Hinglish mixed detection",
        detect_language(
            "Please mujhe ye concept explain karo"
        ) == "hinglish"
    )

    check(
        "Roman Hindi detection",
        detect_language(
            "Mujhe samajh nahi aa raha"
        ) == "hindi"
    )

    # --------------------------------------------------------
    # MIXED INTENT TESTS
    # --------------------------------------------------------

    check(
        "Mixed coding calculator",
        detect_intent(
            "Python mein calculator ka code banao"
        ) == "coding"
    )

    check(
        "Mixed coding weather",
        detect_intent(
            "Python mein weather app ka code banao"
        ) == "coding"
    )

    check(
        "Mixed explanation physics",
        detect_intent(
            "Physics ka concept samjha do"
        ) == "explanation"
    )

    check(
        "Mixed writing teacher",
        detect_intent(
            "Mere teacher ke liye message likh do"
        ) == "writing"
    )

    check(
        "Mixed weather Delhi",
        detect_intent(
            "Delhi ka weather check karo"
        ) == "weather"
    )

    check(
        "Mixed search JEE",
        detect_intent(
            "Google par latest JEE news search karo"
        ) == "search"
    )

    check(
        "Mixed memory",
        detect_intent(
            "Mera ye point yaad rakhna"
        ) == "memory"
    )

    check(
        "Mixed comparison",
        detect_intent(
            "Python vs Java ka difference batao"
        ) == "comparison"
    )

    # --------------------------------------------------------
    # QUESTION TESTS
    # --------------------------------------------------------

    check(
        "Question detection",
        intent_engine.is_question(
            "What is Newton's second law?"
        )
    )

    check(
        "Hindi question detection",
        intent_engine.is_question(
            "Newton ka second law kya hai?"
        )
    )

    # --------------------------------------------------------
    # FOLLOW-UP TEST
    # --------------------------------------------------------

    check(
        "Follow-up detection",
        intent_engine.detect_follow_up(
            "Aur thoda detail mein batao"
        )
    )

    # --------------------------------------------------------
    # TOPIC TESTS
    # --------------------------------------------------------

    check(
        "Physics topic",
        detect_topic(
            "Explain force and acceleration"
        ) == "physics"
    )

    check(
        "Chemistry topic",
        detect_topic(
            "Explain chemical bonding"
        ) == "chemistry"
    )

    check(
        "Mathematics topic",
        detect_topic(
            "Explain binomial theorem"
        ) == "mathematics"
    )

    check(
        "Coding topic",
        detect_topic(
            "Python code banao"
        ) == "coding"
    )

    # --------------------------------------------------------
    # RESULT TESTS
    # --------------------------------------------------------

    result = analyze_intent(
        "Python mein calculator ka code banao"
    )

    check(
        "Target engine mapping",
        result.target_engine == "ai_engine"
    )

    check(
        "Result success",
        result.success is True
    )

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    print("-" * 50)
    print(
        f"Tests passed: {passed}/{total}"
    )

    if passed == total:
        print("INTENT ENGINE TEST PASSED ✅")
        return True

    print("INTENT ENGINE TEST FAILED ❌")
    return False


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    run_tests()