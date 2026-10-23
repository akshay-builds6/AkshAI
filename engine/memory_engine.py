"""
AkshAI Memory Engine v1.0
Long-term memory management with JSON persistence.
"""

import json
import os
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional


ENGINE_NAME = "AkshAI Memory Engine"
ENGINE_VERSION = "1.0"

BASE_DIR = "/storage/emulated/0/AkshAI"
MEMORY_DIR = os.path.join(BASE_DIR, "data")
MEMORY_FILE = os.path.join(MEMORY_DIR, "memory.json")


# ==========================================================
# DATA MODEL
# ==========================================================

@dataclass
class Memory:
    memory_id: str
    content: str
    category: str = "general"
    importance: int = 3
    tags: Optional[List[str]] = None
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

        if not self.created_at:
            self.created_at = datetime.now().isoformat(timespec="seconds")

        if not self.updated_at:
            self.updated_at = self.created_at

        self.importance = max(1, min(5, int(self.importance)))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            memory_id=str(data.get("memory_id", "")),
            content=str(data.get("content", "")),
            category=str(data.get("category", "general")),
            importance=int(data.get("importance", 3)),
            tags=list(data.get("tags", [])),
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", "")),
        )


# ==========================================================
# RESULT MODEL
# ==========================================================

@dataclass
class MemoryResult:
    success: bool
    action: str
    message: str = ""
    memory: Optional[Dict[str, Any]] = None
    memories: Optional[List[Dict[str, Any]]] = None
    count: int = 0
    error: str = ""
    error_type: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ==========================================================
# MEMORY ENGINE
# ==========================================================

class MemoryEngine:

    def __init__(self, memory_file: str = MEMORY_FILE):
        self.memory_file = memory_file
        self.memories: List[Memory] = []
        self._ensure_storage()
        self.load()

    # ------------------------------------------------------
    # STORAGE
    # ------------------------------------------------------

    def _ensure_storage(self):
        directory = os.path.dirname(self.memory_file)

        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        if not os.path.exists(self.memory_file):
            self._write_file([])

    def _write_file(self, data: List[Dict[str, Any]]) -> bool:
        try:
            directory = os.path.dirname(self.memory_file)

            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            temp_file = self.memory_file + ".tmp"

            with open(temp_file, "w", encoding="utf-8") as file:
                json.dump(
                    data,
                    file,
                    ensure_ascii=False,
                    indent=2
                )

            os.replace(temp_file, self.memory_file)
            return True

        except Exception:
            return False

    def _save(self) -> bool:
        return self._write_file(
            [memory.to_dict() for memory in self.memories]
        )

    def load(self) -> MemoryResult:
        try:
            with open(self.memory_file, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, list):
                data = []

            self.memories = []

            for item in data:
                if isinstance(item, dict):
                    try:
                        memory = Memory.from_dict(item)

                        if memory.content.strip():
                            self.memories.append(memory)

                    except Exception:
                        continue

            return MemoryResult(
                success=True,
                action="load",
                message="Memory loaded successfully.",
                count=len(self.memories)
            )

        except Exception as error:
            self.memories = []

            return MemoryResult(
                success=False,
                action="load",
                error=str(error),
                error_type="load_error"
            )

    # ------------------------------------------------------
    # NORMALIZATION
    # ------------------------------------------------------

    @staticmethod
    def normalize(text: str) -> str:
        if not isinstance(text, str):
            return ""

        text = text.strip().lower()
        text = re.sub(r"\s+", " ", text)

        return text

    @staticmethod
    def clean_content(content: str) -> str:
        if not isinstance(content, str):
            return ""

        content = content.strip()
        content = re.sub(r"\s+", " ", content)

        return content

    @staticmethod
    def normalize_tags(tags) -> List[str]:
        if tags is None:
            return []

        if isinstance(tags, str):
            tags = re.split(r"[,;]", tags)

        if not isinstance(tags, (list, tuple, set)):
            return []

        result = []

        for tag in tags:
            tag = str(tag).strip().lower()

            if tag and tag not in result:
                result.append(tag)

        return result

    # ------------------------------------------------------
    # ID GENERATION
    # ------------------------------------------------------

    def _generate_id(self) -> str:
        numbers = []

        for memory in self.memories:
            match = re.search(r"(\d+)$", memory.memory_id)

            if match:
                numbers.append(int(match.group(1)))

        next_number = max(numbers, default=0) + 1

        return f"mem_{next_number:04d}"

    # ------------------------------------------------------
    # ADD
    # ------------------------------------------------------

    def add(
        self,
        content: str,
        category: str = "general",
        importance: int = 3,
        tags=None
    ) -> MemoryResult:

        content = self.clean_content(content)

        if not content:
            return MemoryResult(
                success=False,
                action="add",
                message="Memory content cannot be empty.",
                error="Empty memory content.",
                error_type="invalid_content"
            )

        category = self.clean_content(category) or "general"
        tags = self.normalize_tags(tags)

        # Avoid exact duplicates.
        normalized_content = self.normalize(content)

        for memory in self.memories:
            if self.normalize(memory.content) == normalized_content:
                return MemoryResult(
                    success=False,
                    action="add",
                    message="This memory already exists.",
                    memory=memory.to_dict(),
                    error="Duplicate memory.",
                    error_type="duplicate"
                )

        memory = Memory(
            memory_id=self._generate_id(),
            content=content,
            category=category,
            importance=importance,
            tags=tags
        )

        self.memories.append(memory)

        if not self._save():
            self.memories.pop()

            return MemoryResult(
                success=False,
                action="add",
                error="Could not save memory.",
                error_type="save_error"
            )

        return MemoryResult(
            success=True,
            action="add",
            message="Memory added successfully.",
            memory=memory.to_dict(),
            count=1
        )

    # ------------------------------------------------------
    # GET
    # ------------------------------------------------------

    def get(self, memory_id: str) -> MemoryResult:

        memory_id = str(memory_id).strip()

        for memory in self.memories:
            if memory.memory_id == memory_id:
                return MemoryResult(
                    success=True,
                    action="get",
                    memory=memory.to_dict(),
                    count=1
                )

        return MemoryResult(
            success=False,
            action="get",
            error="Memory not found.",
            error_type="not_found"
        )

    # ------------------------------------------------------
    # SEARCH
    # ------------------------------------------------------

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        tag: Optional[str] = None,
        limit: int = 10
    ) -> MemoryResult:

        query = self.normalize(query)
        category = self.normalize(category) if category else None
        tag = self.normalize(tag) if tag else None

        if not query and not category and not tag:
            return MemoryResult(
                success=False,
                action="search",
                error="Search query cannot be empty.",
                error_type="invalid_query"
            )

        try:
            limit = max(1, int(limit))
        except Exception:
            limit = 10

        query_words = set(query.split())

        recall_phrases = (
            "what did i ask you to remember",
            "what exact code word",
            "what did i tell you to remember",
            "what do you remember about",
        )

        is_recall_question = any(
            phrase in query for phrase in recall_phrases
        )

        if is_recall_question:
            query_words = {
                word for word in query.split()
                if word not in {
                    "what", "did", "i", "ask", "you", "to",
                    "remember", "exact", "code", "word", "tell",
                    "me", "about"
                }
            }

        scored = []

        for memory in self.memories:

            if category:
                if self.normalize(memory.category) != category:
                    continue

            if tag:
                if tag not in self.normalize_tags(memory.tags):
                    continue

            content = self.normalize(memory.content)
            tags = self.normalize_tags(memory.tags)

            score = 0

            if query:
                if query == content:
                    score += 100

                if query in content:
                    score += 50

                content_words = set(content.split())

                score += len(query_words & content_words) * 10

                for memory_tag in tags:
                    if memory_tag in query_words:
                        score += 8

            else:
                score = memory.importance

            if score > 0:
                scored.append((score, memory))

        scored.sort(
            key=lambda item: (
                item[0],
                item[1].importance,
                item[1].updated_at
            ),
            reverse=True
        )

        results = [
            memory.to_dict()
            for _, memory in scored[:limit]
        ]

        return MemoryResult(
            success=True,
            action="search",
            message=f"Found {len(results)} memory item(s).",
            memories=results,
            count=len(results)
        )

    # ------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------

    def update(
        self,
        memory_id: str,
        content: Optional[str] = None,
        category: Optional[str] = None,
        importance: Optional[int] = None,
        tags=None
    ) -> MemoryResult:

        memory_id = str(memory_id).strip()

        target = None

        for memory in self.memories:
            if memory.memory_id == memory_id:
                target = memory
                break

        if target is None:
            return MemoryResult(
                success=False,
                action="update",
                error="Memory not found.",
                error_type="not_found"
            )

        old_data = target.to_dict()

        if content is not None:
            content = self.clean_content(content)

            if not content:
                return MemoryResult(
                    success=False,
                    action="update",
                    error="Memory content cannot be empty.",
                    error_type="invalid_content"
                )

            target.content = content

        if category is not None:
            category = self.clean_content(category)
            target.category = category or "general"

        if importance is not None:
            try:
                target.importance = max(
                    1,
                    min(5, int(importance))
                )
            except Exception:
                target.importance = 3

        if tags is not None:
            target.tags = self.normalize_tags(tags)

        target.updated_at = datetime.now().isoformat(
            timespec="seconds"
        )

        if not self._save():
            target.content = old_data["content"]
            target.category = old_data["category"]
            target.importance = old_data["importance"]
            target.tags = old_data["tags"]
            target.updated_at = old_data["updated_at"]

            return MemoryResult(
                success=False,
                action="update",
                error="Could not save updated memory.",
                error_type="save_error"
            )

        return MemoryResult(
            success=True,
            action="update",
            message="Memory updated successfully.",
            memory=target.to_dict(),
            count=1
        )

    # ------------------------------------------------------
    # DELETE
    # ------------------------------------------------------

    def delete(self, memory_id: str) -> MemoryResult:

        memory_id = str(memory_id).strip()

        for index, memory in enumerate(self.memories):

            if memory.memory_id == memory_id:

                removed = self.memories.pop(index)

                if not self._save():
                    self.memories.insert(index, removed)

                    return MemoryResult(
                        success=False,
                        action="delete",
                        error="Could not save deletion.",
                        error_type="save_error"
                    )

                return MemoryResult(
                    success=True,
                    action="delete",
                    message="Memory deleted successfully.",
                    memory=removed.to_dict(),
                    count=1
                )

        return MemoryResult(
            success=False,
            action="delete",
            error="Memory not found.",
            error_type="not_found"
        )

    # ------------------------------------------------------
    # CLEAR
    # ------------------------------------------------------

    def clear(self) -> MemoryResult:

        old_memories = self.memories.copy()
        self.memories = []

        if not self._save():
            self.memories = old_memories

            return MemoryResult(
                success=False,
                action="clear",
                error="Could not clear memories.",
                error_type="save_error"
            )

        return MemoryResult(
            success=True,
            action="clear",
            message="All memories cleared.",
            count=len(old_memories)
        )

    # ------------------------------------------------------
    # LIST
    # ------------------------------------------------------

    def list_memories(
        self,
        category: Optional[str] = None,
        minimum_importance: int = 1
    ) -> MemoryResult:

        category = self.normalize(category) if category else None

        try:
            minimum_importance = max(
                1,
                min(5, int(minimum_importance))
            )
        except Exception:
            minimum_importance = 1

        results = []

        for memory in self.memories:

            if category:
                if self.normalize(memory.category) != category:
                    continue

            if memory.importance < minimum_importance:
                continue

            results.append(memory.to_dict())

        results.sort(
            key=lambda item: (
                item["importance"],
                item["updated_at"]
            ),
            reverse=True
        )

        return MemoryResult(
            success=True,
            action="list",
            memories=results,
            count=len(results)
        )

    # ------------------------------------------------------
    # IMPORTANT MEMORIES
    # ------------------------------------------------------

    def important(self, minimum_importance: int = 4) -> MemoryResult:

        return self.list_memories(
            minimum_importance=minimum_importance
        )

    # ------------------------------------------------------
    # CATEGORY
    # ------------------------------------------------------

    def categories(self) -> List[str]:

        result = []

        for memory in self.memories:
            category = memory.category

            if category not in result:
                result.append(category)

        return sorted(result)

    # ------------------------------------------------------
    # TAGS
    # ------------------------------------------------------

    def tags(self) -> List[str]:

        result = []

        for memory in self.memories:
            for tag in memory.tags:

                if tag not in result:
                    result.append(tag)

        return sorted(result)

    # ------------------------------------------------------
    # COUNT
    # ------------------------------------------------------

    def count(self) -> int:
        return len(self.memories)

    # ------------------------------------------------------
    # STATUS
    # ------------------------------------------------------

    def status(self) -> Dict[str, Any]:

        category_counts = {}

        for memory in self.memories:
            category = memory.category

            category_counts[category] = (
                category_counts.get(category, 0) + 1
            )

        return {
            "engine": ENGINE_NAME,
            "version": ENGINE_VERSION,
            "memory_file": self.memory_file,
            "memory_count": len(self.memories),
            "categories": len(category_counts),
            "category_counts": category_counts,
            "tags": len(self.tags()),
            "storage_exists": os.path.exists(self.memory_file)
        }


# ==========================================================
# DEFAULT ENGINE
# ==========================================================

_default_engine = MemoryEngine()


# ==========================================================
# PUBLIC FUNCTIONS
# ==========================================================

def add_memory(
    content: str,
    category: str = "general",
    importance: int = 3,
    tags=None
) -> MemoryResult:

    return _default_engine.add(
        content,
        category,
        importance,
        tags
    )


def get_memory(memory_id: str) -> MemoryResult:
    return _default_engine.get(memory_id)


def search_memory(
    query: str,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = 10
) -> MemoryResult:

    return _default_engine.search(
        query,
        category,
        tag,
        limit
    )


def update_memory(
    memory_id: str,
    content: Optional[str] = None,
    category: Optional[str] = None,
    importance: Optional[int] = None,
    tags=None
) -> MemoryResult:

    return _default_engine.update(
        memory_id,
        content,
        category,
        importance,
        tags
    )


def delete_memory(memory_id: str) -> MemoryResult:
    return _default_engine.delete(memory_id)


def clear_memory() -> MemoryResult:
    return _default_engine.clear()


def list_memories(
    category: Optional[str] = None,
    minimum_importance: int = 1
) -> MemoryResult:

    return _default_engine.list_memories(
        category,
        minimum_importance
    )


def important_memories(
    minimum_importance: int = 4
) -> MemoryResult:

    return _default_engine.important(
        minimum_importance
    )


def memory_categories() -> List[str]:
    return _default_engine.categories()


def memory_tags() -> List[str]:
    return _default_engine.tags()


def memory_count() -> int:
    return _default_engine.count()


def memory_status() -> Dict[str, Any]:
    return _default_engine.status()


# ==========================================================
# SELF TEST
# ==========================================================

def run_memory_engine_test() -> bool:

    print("=" * 58)
    print("AkshAI Memory Engine v1.0")
    print("=" * 58)

    test_file = os.path.join(
        MEMORY_DIR,
        "memory_test.json"
    )

    if os.path.exists(test_file):
        try:
            os.remove(test_file)
        except Exception:
            pass

    engine = MemoryEngine(test_file)

    passed = 0
    total = 0

    def check(name, condition):
        nonlocal passed, total

        total += 1

        if condition:
            print(f"{name} passed")
            passed += 1
        else:
            print(f"FAILED {name}")

    # 1
    check(
        "Normalization test",
        engine.normalize("  Hello   AkshAI  ") == "hello akshai"
    )

    # 2
    check(
        "Tag normalization test",
        engine.normalize_tags("JEE, Study, JEE")
        == ["jee", "study"]
    )

    # 3
    result = engine.add(
        "User is studying Class 11 PCM.",
        category="education",
        importance=5,
        tags=["study", "pcm", "jee"]
    )

    check(
        "Add memory test",
        result.success and result.memory["memory_id"] == "mem_0001"
    )

    # 4
    result2 = engine.add(
        "User likes Python programming.",
        category="coding",
        importance=4,
        tags=["python", "coding"]
    )

    check(
        "Second memory test",
        result2.success
    )

    # 5
    duplicate = engine.add(
        "User is studying Class 11 PCM.",
        category="education"
    )

    check(
        "Duplicate detection test",
        not duplicate.success
        and duplicate.error_type == "duplicate"
    )

    # 6
    found = engine.search("PCM")

    check(
        "Search test",
        found.success
        and found.count == 1
        and found.memories[0]["memory_id"] == "mem_0001"
    )

    # 7
    category_search = engine.search(
        "",
        category="coding"
    )

    check(
        "Category search test",
        category_search.success
        and category_search.count == 1
    )

    # 8
    tag_search = engine.search(
        "",
        tag="python"
    )

    check(
        "Tag search test",
        tag_search.success
        and tag_search.count == 1
    )

    # 9
    important = engine.important()

    check(
        "Important memory test",
        important.success
        and important.count == 2
    )

    # 10
    got = engine.get("mem_0001")

    check(
        "Get memory test",
        got.success
        and got.memory["category"] == "education"
    )

    # 11
    updated = engine.update(
        "mem_0001",
        content="User is preparing for JEE.",
        importance=5,
        tags=["jee", "study"]
    )

    check(
        "Update memory test",
        updated.success
        and "JEE" in updated.memory["content"]
        and "jee" in updated.memory["tags"]
    )

    # 12
    found_updated = engine.search("preparing JEE")

    check(
        "Updated search test",
        found_updated.success
        and found_updated.count == 1
    )

    # 13
    categories = engine.categories()

    check(
        "Categories test",
        categories == ["coding", "education"]
    )

    # 14
    tags = engine.tags()

    check(
        "Tags test",
        "jee" in tags
        and "python" in tags
    )

    # 15
    status = engine.status()

    check(
        "Status test",
        status["memory_count"] == 2
        and status["storage_exists"]
    )

    # 16
    deleted = engine.delete("mem_0002")

    check(
        "Delete memory test",
        deleted.success
        and engine.count() == 1
    )

    # 17
    missing = engine.get("mem_9999")

    check(
        "Missing memory test",
        not missing.success
        and missing.error_type == "not_found"
    )

    # 18
    engine2 = MemoryEngine(test_file)

    check(
        "Persistence test",
        engine2.count() == 1
        and engine2.memories[0].memory_id == "mem_0001"
    )

    # 19
    cleared = engine2.clear()

    check(
        "Clear memory test",
        cleared.success
        and engine2.count() == 0
    )

    # 20
    empty_search = engine2.search("nothing")

    check(
        "Empty search result test",
        empty_search.success
        and empty_search.count == 0
    )

    # Cleanup
    try:
        if os.path.exists(test_file):
            os.remove(test_file)
    except Exception:
        pass

    print("-" * 58)
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("MEMORY ENGINE TEST PASSED ✅")
        return True

    print("MEMORY ENGINE TEST FAILED ❌")
    return False


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":
    run_memory_engine_test()