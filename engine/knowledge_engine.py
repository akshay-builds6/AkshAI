"""
============================================================
AkshAI Knowledge Engine v1.0
============================================================

Local knowledge foundation for AkshAI.

This engine:
- Stores structured knowledge
- Searches topics and keywords
- Supports multiple knowledge categories
- Provides confidence scores
- Handles unknown questions
- Allows adding/removing knowledge
- Is designed to work later with AI + Internet engines

Standard library only.
============================================================
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple


# ============================================================
# ENGINE INFORMATION
# ============================================================

ENGINE_NAME = "AkshAI Knowledge Engine"
ENGINE_VERSION = "1.0"
ENGINE_STATUS = "ready"


# ============================================================
# KNOWLEDGE CATEGORIES
# ============================================================

KNOWLEDGE_CATEGORIES = [
    "general",
    "science",
    "physics",
    "chemistry",
    "mathematics",
    "biology",
    "computer_science",
    "coding",
    "history",
    "geography",
    "technology",
    "space",
    "environment",
    "education",
    "language",
    "health",
    "finance",
    "sports",
    "literature",
    "art",
]


# ============================================================
# KNOWLEDGE RESULT
# ============================================================

@dataclass
class KnowledgeResult:
    success: bool
    query: str = ""
    category: str = ""
    topic: str = ""
    answer: str = ""
    confidence: float = 0.0
    source: str = "local"
    needs_external_knowledge: bool = False
    matches: int = 0
    error: str = ""
    error_type: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================
# KNOWLEDGE ENTRY
# ============================================================

@dataclass
class KnowledgeEntry:
    topic: str
    category: str
    keywords: List[str]
    answer: str
    aliases: Optional[List[str]] = None

    def __post_init__(self) -> None:
        if self.aliases is None:
            self.aliases = []

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text: str) -> str:
    """
    Normalize text for searching.
    """

    if not isinstance(text, str):
        return ""

    text = text.lower().strip()

    replacements = {
        "×": " x ",
        "÷": " / ",
        "−": "-",
        "–": "-",
        "—": "-",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(
        r"[^\w\s+\-./%]",
        " ",
        text,
        flags=re.UNICODE
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def tokenize(text: str) -> List[str]:
    """
    Split normalized text into tokens.
    """

    normalized = normalize_text(text)

    if not normalized:
        return []

    return normalized.split()


# ============================================================
# BUILT-IN KNOWLEDGE BASE
# ============================================================

KNOWLEDGE_BASE: List[KnowledgeEntry] = [

    # --------------------------------------------------------
    # GENERAL / TECHNOLOGY
    # --------------------------------------------------------

    KnowledgeEntry(
        topic="Artificial Intelligence",
        category="technology",
        keywords=[
            "artificial intelligence",
            "ai",
            "machine intelligence",
            "intelligent machines",
        ],
        aliases=[
            "what is ai",
            "define ai",
        ],
        answer=(
            "Artificial Intelligence (AI) is a field of "
            "computer science concerned with creating systems "
            "that can perform tasks involving abilities such "
            "as learning, reasoning, perception and language "
            "understanding."
        ),
    ),

    KnowledgeEntry(
        topic="Computer",
        category="computer_science",
        keywords=[
            "computer",
            "computers",
            "computing",
        ],
        aliases=[
            "what is computer",
        ],
        answer=(
            "A computer is an electronic device that accepts "
            "data, processes it according to instructions, "
            "stores information and produces results."
        ),
    ),

    KnowledgeEntry(
        topic="Internet",
        category="technology",
        keywords=[
            "internet",
            "world wide web",
            "web",
        ],
        aliases=[
            "what is internet",
        ],
        answer=(
            "The Internet is a global network of interconnected "
            "computer networks that communicate using standard "
            "communication protocols."
        ),
    ),

    # --------------------------------------------------------
    # PHYSICS
    # --------------------------------------------------------

    KnowledgeEntry(
        topic="Newton's Second Law",
        category="physics",
        keywords=[
            "newton second law",
            "newtons second law",
            "second law of motion",
            "force mass acceleration",
            "f ma",
        ],
        aliases=[
            "what is newton second law",
            "explain newton second law",
        ],
        answer=(
            "Newton's Second Law states that the net force "
            "acting on an object is related to its mass and "
            "acceleration. In SI units, force is measured in "
            "newtons."
        ),
    ),

    KnowledgeEntry(
        topic="Velocity",
        category="physics",
        keywords=[
            "velocity",
            "speed direction",
        ],
        aliases=[
            "what is velocity",
            "define velocity",
        ],
        answer=(
            "Velocity is the rate of change of displacement "
            "with respect to time. It is a vector quantity, "
            "so it has both magnitude and direction."
        ),
    ),

    KnowledgeEntry(
        topic="Acceleration",
        category="physics",
        keywords=[
            "acceleration",
            "accelerated motion",
            "rate of change velocity",
        ],
        aliases=[
            "what is acceleration",
        ],
        answer=(
            "Acceleration is the rate of change of velocity "
            "with respect to time. It is a vector quantity."
        ),
    ),

    KnowledgeEntry(
        topic="Kinetic Energy",
        category="physics",
        keywords=[
            "kinetic energy",
            "energy of motion",
        ],
        aliases=[
            "what is kinetic energy",
        ],
        answer=(
            "Kinetic energy is the energy possessed by an "
            "object because of its motion."
        ),
    ),

    KnowledgeEntry(
        topic="Potential Energy",
        category="physics",
        keywords=[
            "potential energy",
            "gravitational potential energy",
        ],
        aliases=[
            "what is potential energy",
        ],
        answer=(
            "Potential energy is stored energy associated with "
            "an object's position, configuration or condition."
        ),
    ),

    KnowledgeEntry(
        topic="Gravity",
        category="physics",
        keywords=[
            "gravity",
            "gravitation",
            "gravitational force",
        ],
        aliases=[
            "what is gravity",
        ],
        answer=(
            "Gravity is the attractive interaction between "
            "objects with mass. Near Earth's surface, it causes "
            "objects to accelerate downward."
        ),
    ),

    # --------------------------------------------------------
    # CHEMISTRY
    # --------------------------------------------------------

    KnowledgeEntry(
        topic="Atom",
        category="chemistry",
        keywords=[
            "atom",
            "atomic",
            "atomic structure",
        ],
        aliases=[
            "what is atom",
            "define atom",
        ],
        answer=(
            "An atom is the basic unit of a chemical element. "
            "It contains a nucleus made of protons and "
            "neutrons, surrounded by electrons."
        ),
    ),

    KnowledgeEntry(
        topic="Molecule",
        category="chemistry",
        keywords=[
            "molecule",
            "molecular",
        ],
        aliases=[
            "what is molecule",
        ],
        answer=(
            "A molecule is a group of two or more atoms held "
            "together by chemical bonds."
        ),
    ),

    KnowledgeEntry(
        topic="Chemical Bond",
        category="chemistry",
        keywords=[
            "chemical bond",
            "chemical bonding",
            "bond",
            "bonding",
            "ionic bond",
            "covalent bond",
            "metallic bond",
        ],
        aliases=[
            "what is chemical bonding",
            "explain chemical bonding",
        ],
        answer=(
            "A chemical bond is an attractive interaction that "
            "holds atoms or ions together. Major types include "
            "ionic, covalent and metallic bonding."
        ),
    ),

    KnowledgeEntry(
        topic="Periodic Table",
        category="chemistry",
        keywords=[
            "periodic table",
            "chemical elements",
            "elements",
        ],
        aliases=[
            "what is periodic table",
        ],
        answer=(
            "The periodic table organizes chemical elements "
            "according to atomic number and recurring chemical "
            "properties."
        ),
    ),

    KnowledgeEntry(
        topic="Acid",
        category="chemistry",
        keywords=[
            "acid",
            "acids",
            "acidic",
        ],
        aliases=[
            "what is acid",
        ],
        answer=(
            "In the Brønsted-Lowry model, an acid is a substance "
            "that donates a proton. Acids generally have a pH "
            "below 7 in aqueous solution."
        ),
    ),

    KnowledgeEntry(
        topic="Base",
        category="chemistry",
        keywords=[
            "base",
            "bases",
            "basic",
            "alkaline",
        ],
        aliases=[
            "what is base in chemistry",
        ],
        answer=(
            "In the Brønsted-Lowry model, a base is a substance "
            "that accepts a proton. Many basic aqueous solutions "
            "have a pH above 7."
        ),
    ),

    # --------------------------------------------------------
    # MATHEMATICS
    # --------------------------------------------------------

    KnowledgeEntry(
        topic="Derivative",
        category="mathematics",
        keywords=[
            "derivative",
            "differentiation",
            "differentiate",
        ],
        aliases=[
            "what is derivative",
        ],
        answer=(
            "A derivative measures the instantaneous rate of "
            "change of a function with respect to its variable."
        ),
    ),

    KnowledgeEntry(
        topic="Integral",
        category="mathematics",
        keywords=[
            "integral",
            "integration",
        ],
        aliases=[
            "what is integral",
        ],
        answer=(
            "An integral is a mathematical operation associated "
            "with accumulation. A definite integral can represent "
            "signed area under a curve."
        ),
    ),

    KnowledgeEntry(
        topic="Probability",
        category="mathematics",
        keywords=[
            "probability",
            "chance",
            "likelihood",
        ],
        aliases=[
            "what is probability",
        ],
        answer=(
            "Probability is a measure of how likely an event "
            "is to occur, with values ranging from 0 to 1."
        ),
    ),

    KnowledgeEntry(
        topic="Binomial Theorem",
        category="mathematics",
        keywords=[
            "binomial theorem",
            "binomial",
            "binomial expansion",
        ],
        aliases=[
            "what is binomial theorem",
        ],
        answer=(
            "The Binomial Theorem provides a systematic method "
            "for expanding powers of a binomial into a sum of "
            "terms."
        ),
    ),

    KnowledgeEntry(
        topic="Permutation",
        category="mathematics",
        keywords=[
            "permutation",
            "permutations",
            "arrangement",
        ],
        aliases=[
            "what is permutation",
        ],
        answer=(
            "A permutation is an arrangement of objects in which "
            "the order of the selected objects matters."
        ),
    ),

    KnowledgeEntry(
        topic="Combination",
        category="mathematics",
        keywords=[
            "combination",
            "combinations",
            "selection",
        ],
        aliases=[
            "what is combination",
        ],
        answer=(
            "A combination is a selection of objects in which "
            "the order of selection does not matter."
        ),
    ),

    # --------------------------------------------------------
    # BIOLOGY
    # --------------------------------------------------------

    KnowledgeEntry(
        topic="Cell",
        category="biology",
        keywords=[
            "cell",
            "cells",
            "cell biology",
        ],
        aliases=[
            "what is a cell",
            "what is cell biology",
        ],
        answer=(
            "A cell is the basic structural and functional unit "
            "of living organisms."
        ),
    ),

    KnowledgeEntry(
        topic="DNA",
        category="biology",
        keywords=[
            "dna",
            "deoxyribonucleic acid",
            "genetic material",
        ],
        aliases=[
            "what is dna",
        ],
        answer=(
            "DNA, or deoxyribonucleic acid, is the molecule that "
            "stores hereditary genetic information in organisms."
        ),
    ),

    KnowledgeEntry(
        topic="Photosynthesis",
        category="biology",
        keywords=[
            "photosynthesis",
            "photosynthetic",
        ],
        aliases=[
            "what is photosynthesis",
        ],
        answer=(
            "Photosynthesis is a process in which plants, algae "
            "and some microorganisms use light energy to produce "
            "chemical energy from carbon dioxide and water."
        ),
    ),

    # --------------------------------------------------------
    # CODING
    # --------------------------------------------------------

    KnowledgeEntry(
        topic="Python",
        category="coding",
        keywords=[
            "python",
            "python programming",
            "python language",
        ],
        aliases=[
            "what is python programming",
        ],
        answer=(
            "Python is a high-level, general-purpose programming "
            "language known for readable syntax and a large "
            "ecosystem of libraries."
        ),
    ),

    KnowledgeEntry(
        topic="Variable",
        category="coding",
        keywords=[
            "variable",
            "variables",
            "programming variable",
        ],
        aliases=[
            "what is variable in programming",
        ],
        answer=(
            "A variable is a named reference used by a program "
            "to store or refer to a value."
        ),
    ),

    KnowledgeEntry(
        topic="Algorithm",
        category="computer_science",
        keywords=[
            "algorithm",
            "algorithms",
            "algorithmic",
        ],
        aliases=[
            "what is algorithm",
        ],
        answer=(
            "An algorithm is a finite sequence of well-defined "
            "steps used to solve a problem or perform a task."
        ),
    ),

    # --------------------------------------------------------
    # SPACE
    # --------------------------------------------------------

    KnowledgeEntry(
        topic="Solar System",
        category="space",
        keywords=[
            "solar system",
            "planets",
            "sun planets",
        ],
        aliases=[
            "what is solar system",
        ],
        answer=(
            "The Solar System consists of the Sun and objects "
            "gravitationally bound to it, including planets, "
            "dwarf planets, moons, asteroids and comets."
        ),
    ),

    KnowledgeEntry(
        topic="Black Hole",
        category="space",
        keywords=[
            "black hole",
            "black holes",
        ],
        aliases=[
            "what is black hole",
        ],
        answer=(
            "A black hole is a region of spacetime where gravity "
            "is extremely strong. Beyond its event horizon, "
            "nothing can escape to the outside, including light."
        ),
    ),

    # --------------------------------------------------------
    # GEOGRAPHY
    # --------------------------------------------------------

    KnowledgeEntry(
        topic="Earth",
        category="geography",
        keywords=[
            "earth",
            "planet earth",
        ],
        aliases=[
            "what is earth",
        ],
        answer=(
            "Earth is the third planet from the Sun and the "
            "planet known to support life."
        ),
    ),

    # --------------------------------------------------------
    # HISTORY
    # --------------------------------------------------------

    KnowledgeEntry(
        topic="History",
        category="history",
        keywords=[
            "history",
            "historical",
        ],
        aliases=[
            "what is history",
        ],
        answer=(
            "History is the study of past events, societies, "
            "people and processes using available evidence."
        ),
    ),
]


# ============================================================
# KNOWLEDGE ENGINE
# ============================================================

class KnowledgeEngine:

    def __init__(
        self,
        entries: Optional[List[KnowledgeEntry]] = None
    ) -> None:

        if entries is None:
            self.entries = list(KNOWLEDGE_BASE)
        else:
            self.entries = list(entries)

    # --------------------------------------------------------
    # ADD ENTRY
    # --------------------------------------------------------

    def add_entry(
        self,
        topic: str,
        category: str,
        keywords: List[str],
        answer: str,
        aliases: Optional[List[str]] = None
    ) -> KnowledgeEntry:

        entry = KnowledgeEntry(
            topic=topic,
            category=category,
            keywords=keywords,
            answer=answer,
            aliases=aliases or []
        )

        self.entries.append(entry)

        return entry

        # --------------------------------------------------------
    # REMOVE ENTRY
    # --------------------------------------------------------

    def remove_entry(
        self,
        topic: str
    ) -> bool:

        target = normalize_text(topic)

        for index, entry in enumerate(self.entries):

            if normalize_text(entry.topic) == target:
                self.entries.pop(index)
                return True

        return False

    # --------------------------------------------------------
    # FIND TOPIC
    # --------------------------------------------------------

    def find_topic(
        self,
        topic: str
    ) -> Optional[KnowledgeEntry]:

        target = normalize_text(topic)

        for entry in self.entries:

            if normalize_text(entry.topic) == target:
                return entry

        return None

    # --------------------------------------------------------
    # GET CATEGORY
    # --------------------------------------------------------

    def get_category(
        self,
        category: str
    ) -> List[KnowledgeEntry]:

        target = normalize_text(category)

        return [
            entry
            for entry in self.entries
            if normalize_text(entry.category) == target
        ]

    # --------------------------------------------------------
    # SCORE ENTRY
    # --------------------------------------------------------

    def _score_entry(
        self,
        query: str,
        entry: KnowledgeEntry
    ) -> float:

        query_normalized = normalize_text(query)

        if not query_normalized:
            return 0.0

        query_tokens = set(
            tokenize(query_normalized)
        )

        score = 0.0

        topic = normalize_text(entry.topic)

        if topic == query_normalized:
            score += 100.0

        elif topic in query_normalized:
            score += 60.0

        elif query_normalized in topic:
            score += 45.0

        for keyword in entry.keywords:

            keyword_normalized = normalize_text(
                keyword
            )

            if not keyword_normalized:
                continue

            if keyword_normalized == query_normalized:
                score += 80.0

            elif keyword_normalized in query_normalized:
                score += 35.0

            elif query_normalized in keyword_normalized:
                score += 25.0

            keyword_tokens = set(
                tokenize(keyword_normalized)
            )

            overlap = query_tokens.intersection(
                keyword_tokens
            )

            score += 8.0 * len(overlap)

        for alias in entry.aliases or []:

            alias_normalized = normalize_text(
                alias
            )

            if alias_normalized == query_normalized:
                score += 90.0

            elif alias_normalized in query_normalized:
                score += 20.0

        all_entry_text = " ".join(
            [
                entry.topic,
                entry.category,
                *entry.keywords,
                *(entry.aliases or []),
            ]
        )

        entry_tokens = set(
            tokenize(all_entry_text)
        )

        overlap = query_tokens.intersection(
            entry_tokens
        )

        score += 3.0 * len(overlap)

        return score

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 5
    ) -> List[Tuple[KnowledgeEntry, float]]:

        if not isinstance(query, str):
            return []

        if limit <= 0:
            limit = 5

        candidates = self.entries

        if category:
            target = normalize_text(category)

            candidates = [
                entry
                for entry in candidates
                if normalize_text(entry.category)
                == target
            ]

        results = []

        for entry in candidates:

            score = self._score_entry(
                query,
                entry
            )

            if score > 0:
                results.append(
                    (entry, score)
                )

        results.sort(
            key=lambda item: item[1],
            reverse=True
        )

        return results[:limit]

    # --------------------------------------------------------
    # BEST MATCH
    # --------------------------------------------------------

    def best_match(
        self,
        query: str,
        category: Optional[str] = None
    ) -> Optional[Tuple[KnowledgeEntry, float]]:

        results = self.search(
            query=query,
            category=category,
            limit=1
        )

        if not results:
            return None

        return results[0]

    # --------------------------------------------------------
    # ANSWER QUERY
    # --------------------------------------------------------

    def answer_query(
        self,
        query: str,
        category: Optional[str] = None
    ) -> KnowledgeResult:

        if not isinstance(query, str):

            return KnowledgeResult(
                success=False,
                query="",
                error="Invalid query.",
                error_type="invalid_query",
                needs_external_knowledge=True
            )

        query = query.strip()

        if not query:

            return KnowledgeResult(
                success=False,
                query="",
                error="Empty query.",
                error_type="empty_query",
                needs_external_knowledge=True
            )

        match = self.best_match(
            query,
            category
        )

        if match is None:

            return KnowledgeResult(
                success=False,
                query=query,
                category=category or "",
                source="local",
                needs_external_knowledge=True,
                matches=0,
                error="Knowledge not found locally.",
                error_type="knowledge_not_found"
            )

        entry, score = match

        confidence = min(
            1.0,
            score / 100.0
        )

        if confidence < 0.25:

            return KnowledgeResult(
                success=False,
                query=query,
                category=entry.category,
                topic=entry.topic,
                confidence=confidence,
                source="local",
                needs_external_knowledge=True,
                matches=1,
                error="Local match confidence is too low.",
                error_type="low_confidence"
            )

        return KnowledgeResult(
            success=True,
            query=query,
            category=entry.category,
            topic=entry.topic,
            answer=entry.answer,
            confidence=confidence,
            source="local",
            needs_external_knowledge=False,
            matches=1
        )

    # --------------------------------------------------------
    # TOPICS
    # --------------------------------------------------------

    def topics(
        self,
        category: Optional[str] = None
    ) -> List[str]:

        if category:
            entries = self.get_category(
                category
            )
        else:
            entries = self.entries

        return [
            entry.topic
            for entry in entries
        ]

    # --------------------------------------------------------
    # COUNT
    # --------------------------------------------------------

    def count(
        self,
        category: Optional[str] = None
    ) -> int:

        if category:
            return len(
                self.get_category(category)
            )

        return len(self.entries)

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    def status(self) -> Dict[str, Any]:

        category_counts: Dict[str, int] = {}

        for category in KNOWLEDGE_CATEGORIES:

            count = len(
                self.get_category(category)
            )

            if count > 0:
                category_counts[
                    category
                ] = count

        return {
            "engine": ENGINE_NAME,
            "version": ENGINE_VERSION,
            "status": ENGINE_STATUS,
            "entries": len(self.entries),
            "categories": len(category_counts),
            "category_counts": category_counts,
            "local_knowledge": True,
            "external_knowledge_supported": True,
        }


# ============================================================
# DEFAULT ENGINE INSTANCE
# ============================================================

_default_engine = KnowledgeEngine()


# ============================================================
# PUBLIC FUNCTIONS
# ============================================================

def search_knowledge(
    query: str,
    category: Optional[str] = None,
    limit: int = 5
) -> List[Tuple[KnowledgeEntry, float]]:

    return _default_engine.search(
        query=query,
        category=category,
        limit=limit
    )


def get_knowledge(
    query: str,
    category: Optional[str] = None
) -> KnowledgeResult:

    return _default_engine.answer_query(
        query=query,
        category=category
    )


def add_knowledge(
    topic: str,
    category: str,
    keywords: List[str],
    answer: str,
    aliases: Optional[List[str]] = None
) -> KnowledgeEntry:

    return _default_engine.add_entry(
        topic=topic,
        category=category,
        keywords=keywords,
        answer=answer,
        aliases=aliases
    )


def remove_knowledge(
    topic: str
) -> bool:

    return _default_engine.remove_entry(
        topic
    )


def get_knowledge_status() -> Dict[str, Any]:

    return _default_engine.status()


# ============================================================
# SELF TEST
# ============================================================

def run_self_test() -> bool:

    print("=" * 58)
    print("AkshAI Knowledge Engine v1.0")
    print("=" * 58)

    passed = 0
    total = 0

    def check(
        name: str,
        condition: bool
    ) -> None:

        nonlocal passed
        nonlocal total

        total += 1

        if condition:
            passed += 1
            print(
                f"{name} test passed"
            )
        else:
            print(
                f"FAILED {name}"
            )

    # --------------------------------------------------------
    # NORMALIZATION
    # --------------------------------------------------------

    check(
        "Text normalization",
        normalize_text(
            "  Hello   AkshAI!  "
        ) == "hello akshai"
    )

    check(
        "Tokenization",
        tokenize(
            "Newton Second Law"
        )
        == [
            "newton",
            "second",
            "law"
        ]
    )

    # --------------------------------------------------------
    # CATEGORY TESTS
    # --------------------------------------------------------

    check(
        "Physics category",
        len(
            _default_engine.get_category(
                "physics"
            )
        ) > 0
    )

    check(
        "Chemistry category",
        len(
            _default_engine.get_category(
                "chemistry"
            )
        ) > 0
    )

    check(
        "Mathematics category",
        len(
            _default_engine.get_category(
                "mathematics"
            )
        ) > 0
    )

    # --------------------------------------------------------
    # TOPIC LOOKUP
    # --------------------------------------------------------

    atom = _default_engine.find_topic(
        "Atom"
    )

    check(
        "Topic lookup",
        (
            atom is not None
            and atom.category == "chemistry"
        )
    )

    # --------------------------------------------------------
    # SEARCH TESTS
    # --------------------------------------------------------

    chemistry_results = _default_engine.search(
        "chemical bonding"
    )

    check(
        "Chemistry search",
        (
            len(chemistry_results) > 0
            and chemistry_results[0][0].topic
            == "Chemical Bond"
        )
    )

    physics_results = _default_engine.search(
        "Newton second law"
    )

    check(
        "Physics search",
        (
            len(physics_results) > 0
            and physics_results[0][0].topic
            == "Newton's Second Law"
        )
    )

    coding_results = _default_engine.search(
        "Python programming"
    )

    check(
        "Coding search",
        (
            len(coding_results) > 0
            and coding_results[0][0].topic
            == "Python"
        )
    )

    maths_results = _default_engine.search(
        "binomial theorem"
    )

    check(
        "Mathematics search",
        (
            len(maths_results) > 0
            and maths_results[0][0].topic
            == "Binomial Theorem"
        )
    )

    # --------------------------------------------------------
    # ANSWER TESTS
    # --------------------------------------------------------

    atom_answer = _default_engine.answer_query(
        "What is an atom?"
    )

    check(
        "Atom answer",
        (
            atom_answer.success is True
            and atom_answer.topic == "Atom"
            and atom_answer.answer != ""
            and atom_answer.source == "local"
        )
    )

    bonding_answer = _default_engine.answer_query(
        "Explain chemical bonding"
    )

    check(
        "Chemistry answer",
        (
            bonding_answer.success is True
            and bonding_answer.topic
            == "Chemical Bond"
        )
    )

    python_answer = _default_engine.answer_query(
        "What is Python?"
    )

    check(
        "Coding answer",
        (
            python_answer.success is True
            and python_answer.topic == "Python"
        )
    )

    # --------------------------------------------------------
    # UNKNOWN QUERY
    # --------------------------------------------------------

    unknown = _default_engine.answer_query(
        "Tell me something about "
        "xyzabc123 completely unknown object"
    )

    check(
        "Unknown knowledge handling",
        (
            unknown.success is False
            and unknown.needs_external_knowledge
            is True
        )
    )

    # --------------------------------------------------------
    # ADD KNOWLEDGE
    # --------------------------------------------------------

    test_engine = KnowledgeEngine()

    before_count = test_engine.count()

    test_engine.add_entry(
        topic="Test Topic",
        category="general",
        keywords=[
            "test topic",
            "testing"
        ],
        answer="This is a test knowledge entry.",
        aliases=[
            "what is test topic"
        ]
    )

    after_count = test_engine.count()

    check(
        "Add knowledge",
        after_count == before_count + 1
    )

    added_result = test_engine.answer_query(
        "What is test topic?"
    )

    check(
        "Added knowledge search",
        (
            added_result.success is True
            and added_result.topic
            == "Test Topic"
        )
    )

    # --------------------------------------------------------
    # REMOVE KNOWLEDGE
    # --------------------------------------------------------

    removed = test_engine.remove_entry(
        "Test Topic"
    )

    check(
        "Remove knowledge",
        (
            removed is True
            and test_engine.find_topic(
                "Test Topic"
            ) is None
        )
    )

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    status = _default_engine.status()

    check(
        "Status test",
        (
            status["engine"]
            == ENGINE_NAME
            and status["version"]
            == ENGINE_VERSION
            and status["entries"] > 0
            and status[
                "external_knowledge_supported"
            ] is True
        )
    )

    # --------------------------------------------------------
    # RESULT MODEL
    # --------------------------------------------------------

    result = KnowledgeResult(
        success=True,
        query="test",
        category="general",
        topic="Test",
        answer="Test answer",
        confidence=0.9
    )

    result_dict = result.to_dict()

    check(
        "Result model test",
        (
            isinstance(
                result_dict,
                dict
            )
            and result_dict["success"]
            is True
            and result_dict["confidence"]
            == 0.9
        )
    )

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    print("-" * 58)
    print(
        f"Tests passed: {passed}/{total}"
    )

    if passed == total:

        print(
            "KNOWLEDGE ENGINE TEST PASSED ✅"
        )

        return True

    print(
        "KNOWLEDGE ENGINE TEST FAILED ❌"
    )

    return False


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    run_self_test()